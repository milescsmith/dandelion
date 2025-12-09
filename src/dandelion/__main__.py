#! /usr/bin/python
import argparse
import os
import shutil
from pathlib import Path
from typing import Annotated, Literal

import numpy as np
import pandas as pd
import scanpy as sc
import typer
from scanpy import logging as logg

import dandelion as ddl

sc.settings.verbosity = 3

ddl_typer = typer.Typer(
    name="dandelion",
    add_completion=False,
    no_args_is_help=True,
    add_help_option=True,
    rich_markup_mode="rich",
)

@ddl_typer.command(no_args_is_help=True)
def dandelion_preprocess(
    metadata_file: Annotated[
        Path | None,
        typer.Option(
            "--meta",
            help=(
                "Optional metadata CSV file, header required, first column for "
                "sample ID matching folder names in the directory this is being "
                'ran in. Can have a "prefix"/"suffix" column for barcode '
                'alteration, and "individual" to provide tigger groupings that '
                "isn't analysing all of the samples jointly."
            ),
        ),
    ] = None,
    chain: Annotated[
        Literal["tr", "ig"],
        typer.Option(
            "--chain",
            help="Whether the data is TR or IG, as the preprocessing pipelines differ.",
        ),
    ] = "ig",
    org: Annotated[
        str,
        typer.Option(
            "--org",
            help=("organism for running the reannotation. human or mouse."),
        ),
    ] = "human",
    file_prefix: Annotated[
        str,
        typer.Option(
            "--file_prefix",
            help=(
                "Which set of contig files to take for the folder. For a given "
                "PREFIX, will use PREFIX_contig_annotations.csv and "
                'PREFIX_contig.fasta. Defaults to "all".'
            ),
        ),
    ] = "all",
    db: Annotated[
        str,
        typer.Option(
            "--db",
            help=("Which database to use for reannotation. imgt or ogrdb."),
        ),
    ] = "imgt",
    strain: Annotated[
        str | None,
        typer.Option(
            help="Which mouse strain to use for running the reannotation. Only for ogrdb. Defaults to all (None) mouse strains."
        ),
    ] = None,
    sep: Annotated[
        str,
        typer.Option(
            "--sep",
            help="The separator to place between the barcode and prefix/suffix. Uses sample names as a prefix for BCR data if metadata CSV file absent and more than one sample to process.",
        ),
    ] = "_",
    flavour: Annotated[
        str,
        typer.Option(
            "--flavour",
            help='The "flavour" for running igblastn reannotation. Accepts either "strict" or "original". strict will enforce evalue and penalty cutoffs.',
        ),
    ] = "strict",
    filter_to_high_confidence: Annotated[
        bool,
        typer.Option(
            "--filter_to_high_confidence",
            help=(
                "If passed, limits the contig space to ones that are set to 'True' in the high_confidence column of the contig annotation."
            )
        )
    ] = False,
    keep_trailing_hyphen_number: Annotated[
        bool,
        typer.Option(
            "--keep_trailing_hyphen_number",
            help=(
                "If passed, do not strip out the trailing hyphen number, e.g. '-1', from the end of barcodes."
            ),
        ),
    ] = True,
    skip_format_header: Annotated[
        bool,
        typer.Option(
            "--skip_format_header",
            help=("If passed, skips formatting of contig headers."),
        ),
    ] = False,
    skip_tigger: Annotated[
        bool,
        typer.Option(
            "--skip_tigger",
            help=("If passed, skips TIgGER reassign alleles step."),
        ),
    ] = False,
    skip_reassign_dj: Annotated[
        bool,
        typer.Option(
            "--skip_reassign_dj",
            help="If passed, skips reassigning d/j calls with blastn when flavour=strict.",
        ),
    ] = True,
    skip_correct_c: Annotated[
        bool,
        typer.Option(
            "--skip_correct_c",
            help=(
                "If passed, skips correcting c calls at assign_isotypes stage. Only if Chain == IG."
            ),
        ),
    ] = True,
    clean_output: Annotated[
        bool,
        typer.Option(
            "--clean_output",
            help="If passed, remove intermediate files that aren't the primary output from the run reults. The intermediate files may be occasionally useful for inspection.",
        ),
    ] = False,
):
    """Main dandelion-preprocess."""

    # convert loci to lower case for compatibility, and ensure it's in TR/IG
    chain = chain.lower()

    # if args.chain not in ["tr", "ig"]:
    #     raise ValueError("Chain must be TR or IG")

    logg.info("Software versions:\n")
    ddl.logging.print_header()
    # sponge up command line arguments to begin with
    start = logg.info("\nBegin preprocessing\n")

    logg.info(
        "command line parameters:\n",
        deep=(
            f"--------------------------------------------------------------\n"
            f"    --meta = {metadata_file}\n"
            f"    --chain = {chain}\n"
            f"    --org = {org}\n"
            f"    --file_prefix = {file_prefix}\n"
            f"    --db = {db}\n"
            f"    --strain = {str(strain)}\n"
            f"    --sep = {sep}\n"
            f"    --flavour = {flavour}\n"
            f"    --filter_to_high_confidence = {filter_to_high_confidence}\n"
            f"    --keep_trailing_hyphen_number = {keep_trailing_hyphen_number}\n"
            f"    --skip_format_header = {skip_format_header}\n"
            f"    --skip_tigger = {skip_tigger}\n"
            f"    --skip_reassign_dj = {skip_reassign_dj}\n"
            f"    --skip_correct_c = {skip_correct_c}\n"
            f"    --clean_output = {clean_output}\n"
            f": --------------------------------------------------------------\n"
        ),
    )

    # set up a sample list
    # do we have metadata?
    if metadata_file is not None:
        # if so, read it and use the index as the sample list
        meta = pd.read_csv(metadata_file, index_col=0)
        samples = [Path(s) for s in meta]
        if "individual" in meta.columns:
            individuals = list(meta["individual"])
            if not skip_tigger:
                if any(ind in samples for ind in individuals):
                    if clean_output:
                        msg = "Individuals in metadata file must not be the same as sample names when `--clean_output` flag is used. Otherwise, your sample folders will be deleted. Please rename the individual or sample folders, or run without `--clean_output`."
                        raise ValueError(msg)
    else:
        # no metadata file. create empty data frame so we can easily check for
        # column presence
        meta = pd.DataFrame()
        # get list of all subfolders in current folder and run with that
        samples = []
        for item in Path.cwd().iterdir():
            if item.is_dir():
                if not str(item).startswith(
                    "."
                ):  # exclude hidden folders like .ipynb_checkpoints
                    samples.append(item)

    # STEP ONE - ddl.pp.format_fastas()
    # do we have a prefix/suffix?
    if not skip_format_header:
        if "prefix" in meta.columns:
            # process with prefix
            vals = list(meta["prefix"].values)
            ddl.pp.format_fastas(
                samples,
                prefix=vals,
                sep=sep,
                high_confidence_filtering=filter_to_high_confidence,
                remove_trailing_hyphen_number=keep_trailing_hyphen_number,
                filename_prefix=file_prefix,
            )
        elif "suffix" in meta.columns:
            # process with suffix
            vals = list(meta["suffix"].values)
            ddl.pp.format_fastas(
                samples,
                suffix=vals,
                sep=sep,
                high_confidence_filtering=filter_to_high_confidence,
                remove_trailing_hyphen_number=keep_trailing_hyphen_number,
                filename_prefix=file_prefix,
            )
        else:
            # neither. tag with the sample names as default, if more than one
            # sample and the data is IG
            if (len(samples) > 1) and (chain == "ig"):
                ddl.pp.format_fastas(
                    samples,
                    prefix=samples,
                    sep=sep,
                    high_confidence_filtering=filter_to_high_confidence,
                    remove_trailing_hyphen_number=keep_trailing_hyphen_number,
                    filename_prefix=file_prefix,
                )
            else:
                # no need to tag as it's a single sample.
                ddl.pp.format_fastas(
                    samples,
                    high_confidence_filtering=filter_to_high_confidence,
                    remove_trailing_hyphen_number=keep_trailing_hyphen_number,
                    filename_prefix=file_prefix,
                )
    else:
        ddl.pp.format_fastas(
            samples,
            high_confidence_filtering=filter_to_high_confidence,
            remove_trailing_hyphen_number=False,
            filename_prefix=file_prefix,
        )

    # STEP TWO - ddl.pp.reannotate_genes()
    # no tricks here
    ddl.pp.reannotate_genes(
        samples,
        loci=chain,
        org=org,
        filename_prefix=file_prefix,
        flavour=flavour,
        reassign_dj=skip_reassign_dj,
        db=db,
        strain=strain,
    )

    # IG requires further preprocessing, TR is done now
    if chain == "ig":
        if not skip_tigger:
            # STEP THREE - ddl.pp.reassign_alleles()
            # do we have individual information
            if "individual" in meta.columns:
                # run the function for each individual separately
                for ind in np.unique(meta["individual"]):
                    # yes, this screwy thing is needed so the function ingests it
                    # correctly, sorry
                    ddl.pp.reassign_alleles(
                        [str(i) for i in meta[meta["individual"] == ind].index.values],
                        combined_folder=ind,
                        org=org,
                        save_plot=True,
                        show_plot=False,
                        filename_prefix=file_prefix,
                        db=db,
                        strain=strain,
                    )
                    # remove if cleaning output - the important information is
                    # ported to sample folders already
                    if clean_output:
                        os.system("rm -r " + str(ind))
            else:
                # run on the whole thing at once
                ddl.pp.reassign_alleles(
                    samples,
                    combined_folder="tigger",
                    org=org,
                    save_plot=True,
                    show_plot=False,
                    filename_prefix=file_prefix,
                    db=db,
                    strain=strain,
                )
                # remove if cleaning output - the important information is ported
                # to sample folders already
                if clean_output:
                    os.system("rm -r tigger")

        # STEP FOUR - ddl.pp.assign_isotypes()
        # also no tricks here
        # only imgt here, there's no ogrdb c references afaik.
        ddl.pp.assign_isotypes(
            samples,
            org=org,
            save_plot=True,
            show_plot=False,
            filename_prefix=file_prefix,
            correct_c_call=skip_correct_c,
            # correction_dict=correction_dict, # TODO: next time, maybe provide path to fasta file so that this can be used?
        )
        # STEP FIVE - ddl.pp.quantify_mutations()
        # this adds the mu_count and mu_freq columns into the table
        for s in samples:
            samp_path = Path(s) / "dandelion" / f"{file_prefix}_contig_dandelion.tsv"
            if skip_tigger:
                ddl.pp.create_germlines(
                    vdj_data=samp_path,
                    org=org,
                    db=db,
                    strain=strain,
                    save=samp_path,
                )
            ddl.pp.quantify_mutations(samp_path)
            ddl.pp.quantify_mutations(
                samp_path,
                frequency=True,
            )

    # at this stage it's safe to remove the per-sample dandelion/tmp folder if
    # need be
    if clean_output:
        for sample in samples:
            tmp_path = Path(sample) / "dandelion" / "tmp"
            shutil.rmtree(tmp_path)
    logg.info("Pre-processing finished.\n", time=start)
