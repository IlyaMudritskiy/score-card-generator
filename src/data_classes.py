from dataclasses import dataclass, field


@dataclass
class OMDMParam:
    # Basic OMDM param from parsing model.txt
    omdm_name: str
    _type: str


@dataclass
class ExcelParam:
    name: list = field(default_factory=list)
    method: list = field(default_factory=list)


@dataclass
class FullParam(OMDMParam):
    # Extended OMDM param with name in card and method in xlsx
    pmml_name: str
    method: str


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



# TODO - Class for excel search result

@dataclass
class XlsxSearchRes:
    xlsx_name: str
    method: str
