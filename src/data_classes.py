from dataclasses import dataclass

@dataclass
class Param:
    omdm_name: str = ""
    pmml_name: str = ""
    param_type: str = ""
    method: str = ""


@dataclass
class XlsxSearchRes:
    xlsx_name: str
    method: str


@dataclass
class Files:
    xlsx: str
    txt: str
    pmml: list


@dataclass
class PMMLCard:
    score_name: str
    params: list