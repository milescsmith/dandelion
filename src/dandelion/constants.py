from enum import StrEnum

from numpy import nan
from pandas import NA


class ChainType(StrEnum):
    tr = "tr"
    ig = "ig"

class OrgSpecies(StrEnum):
    human = "human"
    mouse = "mouse"

class DBSource(StrEnum):
    imgt = "imgt"
    ogrdb = "ogrdb"

class ReannotateFlavour(StrEnum):
    strict = "strict"
    original = "original"

class MouseStrain(StrEnum):
    c57bl6 = "c57bl6"
    balbc = "balbc"
    _129S1_SvImJ = "129S1_SvImJ"
    AKR_J = "AKR_J"
    A_J = "A_J"
    BALB_c_ByJ = "BALB_c_ByJ"
    BALB_c = "BALB_c"
    C3H_HeJ = "C3H_HeJ"
    C57BL_6J = "C57BL_6J"
    C57BL_6 = "C57BL_6"
    CAST_EiJ = "CAST_EiJ"
    CBA_J = "CBA_J"
    DBA_1J = "DBA_1J"
    DBA_2J = "DBA_2J"
    LEWES_EiJ = "LEWES_EiJ"
    MRL_MpJ = "MRL_MpJ"
    MSM_MsJ = "MSM_MsJ"
    NOD_ShiLtJ = "NOD_ShiLtJ"
    NOR_LtJ = "NOR_LtJ"
    NZB_BlNJ = "NZB_BlNJ"
    PWD_PhJ = "PWD_PhJ"
    SJL_J = "SJL_J"

TRUES = ["T", "t", "True", "true", "TRUE", True, "1"]
FALSES = ["F", "f", "False", "false", "FALSE", False, "0"]
HEAVYLONG = ["IGH", "TRB", "TRD"]
LIGHTSHORT = ["IGK", "IGL", "TRA", "TRG"]
VCALL = "v_call"
JCALL = "j_call"
VCALLG = "v_call_genotyped"
JCALLG = "j_call_genotyped"
STRIPALLELENUM = "[*][0-9][0-9]"
NO_DS = [
    "129S1_SvImJ",
    "AKR_J",
    "A_J",
    "C3H_HeJ",
    "C57BL_6J",
    "BALB_c_ByJ",
    "CBA_J",
    "DBA_1J",
    "DBA_2J",
    "MRL_MpJ",
    "NOR_LtJ",
    "NZB_BlNJ",
    "SJL_J",
]
EMPTIES = [
    None,
    nan,
    NA,
    "nan",
    "NaN",
    "",
]
DEFAULT_PREFIX = "all"
BOOLEAN_LIKE_COLUMNS = ["extra", "ambiguous"]
