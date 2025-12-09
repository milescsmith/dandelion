FROM index.docker.io/astral/uv:python3.12-trixie-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LLVM_VERSION=19
ENV DANDELION_VERSION=0.6.1

RUN apt update -qq \
    && apt install aptitude -y \
    && aptitude install -y \
        ca-certificates \
        curl \
        gnupg \
        dirmngr \
        build-essential \
        wget \
        clang-tidy-$LLVM_VERSION \
        clang-format-$LLVM_VERSION \
        clang-tools-$LLVM_VERSION \
        llvm-$LLVM_VERSION-dev \
        lld-$LLVM_VERSION \
#         lldb-$LLVM_VERSION \
#         llvm-$LLVM_VERSION-tools \
#         libomp-$LLVM_VERSION-dev \
#         libc++-$LLVM_VERSION-dev \
#         libc++abi-$LLVM_VERSION-dev \
#         libclang-common-$LLVM_VERSION-dev \
#         libclang-$LLVM_VERSION-dev \
#         libclang-cpp$LLVM_VERSION-dev \
#         libunwind-$LLVM_VERSION-dev \
#         libclang-rt-$LLVM_VERSION-dev \
#         libpolly-$LLVM_VERSION-dev \
    && gpg --keyserver keyserver.ubuntu.com --recv-key '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' \
    && gpg --armor --export '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' | tee /etc/apt/trusted.gpg.d/cran_debian_key.asc \
    && echo 'deb [signed-by=/etc/apt/trusted.gpg.d/cran_debian_key.asc] http://cloud.r-project.org/bin/linux/debian trixie-cran40/' >> /etc/apt/sources.list.d/sources.list \
    && apt modernize-sources --assume-yes \
    && aptitude update \
    && aptitude full-upgrade -y \
    && aptitude install -y \
    cmake \
    git \
    libcurl4-openssl-dev \
    r-base \
    ncbi-blast+ \
#         clang \
#         gdb \
#         libbz2-dev \
#         libcairo2-dev \
#         libfribidi-dev \
#         libfreetype-dev \
#         libharfbuzz-dev \
#         libhdf5-dev \
#         libffi-dev \
#         liblapack-dev \
#         liblzma-dev \
#         libncurses5-dev \
#         libomp-dev \
#         libopenblas-dev \
#         libpng-dev \
#         libgdbm-dev \
#         libjpeg-dev \
#         libreadline-dev \
#         libtiff5-dev \
#         libsqlite3-dev \
#         libssl-dev \
#         liblzma-dev \
#         lcov \
#         lzma \
#         r-base-dev \
#         sudo \
#         vim \
#         xvfb \
#         zstd \
#         python3-graph-tool \
#         igblast
    && aptitude autoclean \
        && aptitude clean \
        && rm -rf /tmp/downloaded_packages/* \
        && rm -rf /var/lib/apt/lists/*

COPY scripts/setup_libraries.sh /share/setup_libraries.sh
# COPY scripts/dandelion_preprocess.py /share/dandelion_preprocess.py
# COPY scripts/changeo_clonotypes.py /share/changeo_clonotypes.py
COPY scripts/prepare_imgt_database.py /share/prepare_imgt_database.py
COPY scripts/prepare_ogrdb_database.py /share/prepare_ogrdb_database.py
COPY scripts/utils.py /share/utils.py
COPY tests /tests
COPY requirements.txt /share/requirements.txt
COPY sc_dandelion-${DANDELION_VERSION}.dev0+dirty-py3-none-any.whl /share/sc_dandelion-${DANDELION_VERSION}.dev0+dirty-py3-none-any.whl

RUN uv pip install --no-cache --compile-bytecode --system --requirements /share/requirements.txt \
    && uv pip install --no-cache --compile-bytecode --system /share/sc_dandelion-${DANDELION_VERSION}.dev0+dirty-py3-none-any.whl

# Unsure why, but attempting to install all packages in one go failed
# TODO: use renv
RUN Rscript -e "install.packages('BiocManager')" \
  && Rscript -e "BiocManager::install(c('Biostrings', 'Rsamtools', 'cigarillo', 'GenomicAlignments'))" \
  && Rscript -e "BiocManager::install(c('stringi', 'optparse', 'tigger', 'shazam', 'airr', 'alakazam'))"

ENV GERMLINE=/share/database/germlines/
ENV IGDATA=/share/database/igblast/
ENV BLASTDB=/share/database/blast/

RUN chmod +x /share/setup_libraries.sh && /share/setup_libraries.sh \
  && /etc/profile.d/igblast.sh \
  && python /share/prepare_imgt_database.py --makeblastdb /usr/bin/makeblastdb --outdir /share/database --igblast_dir /share/ncbi-igblast \
  && python /share/prepare_ogrdb_database.py --outdir /share/database --makeblastdb /usr/bin/makeblastdb