from dataclasses import dataclass


@dataclass
class OMDMParam:
    # Basic OMDM param from parsing model.txt
    omdm_name: str
    _type: str


@dataclass
class FullParam(OMDMParam):
    # Extended OMDM param with name in card and method in xlsx
    pmml_name: str = ""
    method: str = ""


@dataclass
class Files:
    # Stores files for use
    xlsx: str
    txt: str
    pmml: list


@dataclass
class PMMLCard:
    # Needed info from pmml score card
    score_name: str
    params: list






@dataclass
class XlsxSearchRes:
    xlsx_name: str
    method: str
