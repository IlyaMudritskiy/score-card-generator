from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import os
from pprint import pprint

import pandas

from src.data_classes import OMDMParam, FullParam, PMMLCard,ExcelParam, Files, PMMLCardExt
from src.dir_handler import DirHandler
from src.settings import get_logger


log = get_logger("params_handler.log")


@dataclass
class PMMLExtractor:

    pmml_files: list = field(default_factory=list)
    full_pmml_data: list[PMMLCard] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Write data parsed from ALL .pmml files to class property on creation
        self.full_pmml_data = self.parse_all_pmml()

    def get_pmml_data(self, filename: str) -> PMMLCard:
        """
        Parse ONE pmml card!

        Return PMMLCard instance:

            score_name: str "INC00_NAME"
            params: list ['PARAM_1', 'PARAM_2', 'PARAM_3', 'PARAM_4']
        """

        params = []
        score_name = ""
        param_str = '<DataField dataType="'
        score_str = '<RegressionModel functionName="'

        try:
            with open(filename, "r") as pmml:
                for line in pmml.readlines():
                    if param_str in line:
                        root = ET.fromstring(line)
                        params.append(root.attrib["name"])
                    if score_str in line:
                        for _ in line.split(" "):
                            if "modelName" in _:
                                score_name = _.split('"')[1]

        except Exception as e:
            log.error(e)
        
        result = PMMLCard(score_name, params)
        return result

    def parse_all_pmml(self) -> list[PMMLCard]:
        """
        Parse ALL pmml files!

        Return list of PMMLCard classes
        """
        all_pmml_data = []

        for pmml_file in self.pmml_files:
            all_pmml_data.append(self.get_pmml_data(pmml_file))

        return all_pmml_data

@dataclass
class OMDMExtractor:

    filename: str
    model_params: list[OMDMParam] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.model_params = self.get_omdm_params()

    def get_omdm_params(self) -> list[OMDMParam]:

        """
        Return list of list:
        [
            ['param_1', 'decimal'], 
            ['Param_2', 'decimal'], 
            ['PARAM_3', 'string'], 
            ['ParAm_4', 'string']
        ]
        """

        result = []
        args = {}
        params_list = []

        try:
            # Open model.txt to get OMDM params
            with open(self.filename, "r") as f:

                for line in f.readlines():
                    params = []

                    # From: <xs:attribute name="param_1" type="xs:decimal" use="optional"/>
                    # To: name="param_1", type="xs:decimal"
                    for _ in line.split(" ")[1:3]:
                        # From: name="param_1", type="xs:decimal"
                        # To: param_1, xs:decimal
                        params.append(_.split('"')[1])

                    params_list.append(params)

            for value in params_list:
                # Name
                args["name"] = value[0]

                # From: xs:decimal
                # To: decimal
                args["_type"] = value[1].split(":")[1]
                
                result.append(OMDMParam(**args))
                
        except Exception as e:
            log.error(e)

        return result

    def find_omdm_param(self, name: str) -> OMDMParam:
        for param in self.model_params:
            if param.name.lower() == name.lower():
                return param


@dataclass
class XlsxExtractor:

    filename: str
    sheet: pandas.DataFrame = pandas.DataFrame()

    def __post_init__(self):
        self.sheet = self.parse_xlsx()

    def parse_xlsx(self) -> pandas.DataFrame:
        """Return a DataFrame object with excel sheet content."""

        xlsx_sheet = pandas.DataFrame()

        try:
            xlsx_sheet = pandas.read_excel(self.filename, sheet_name='Data')
            log.debug(f"OK - File '{self.filename}' was parsed into dataframe.")

        except Exception as e:
            log.error(e)

        return xlsx_sheet

    def find_param_in_xlsx(self, param: str) -> pandas.DataFrame:
        """Return a DataFrame object with all occurances of inputed param."""

        # All cases of param (PARAM, param, Param)
        param_query = [param.upper(), param.lower(), param]

        try:
            result = self.sheet.loc[self.sheet['Var_Name'].isin(param_query)]
            
        except Exception as e:
            log.error(e)

        return result

    def get_param_info(self, param_name: str) -> ExcelParam:
        """Return ExcelParam instance with name and method from all occurances in excel."""

        param_info = {}

        try:
            excel_info = self.find_param_in_xlsx(param_name).to_dict()

        except Exception as e:
            log.error(e)

        # Get all param info from find_param response
        var_name = list(excel_info["Var_Name"].values())
        var_methods = list(excel_info["OMDM Data_Method"].values())

        # Check if "Var_Name" is empty
        if not var_name:
            log.error(f"Parameter {param_name} was not found.")

        # Delete duplicates from name and method and pack into dict
        if var_name:

            # Delete duplicates of param name and get it as str
            param_name = list(dict.fromkeys(var_name))[0]

            # Delete duplicates of param method 
            param_method = list(dict.fromkeys(var_methods))

            # Check if there is more than one method for param
            if len(param_method) > 1:
                log.error(f"For '{param_name}' exists more than one method!")

            # Get param method as string
            if len(param_method) == 1:
                param_method = param_method[0]

            param_info["name"] = param_name
            param_info["method"] = param_method

        return ExcelParam(**param_info)


@dataclass
class ParamsCombiner:

    excel_data: XlsxExtractor = None
    omdm_data: OMDMExtractor = None
    pmml_data: PMMLExtractor = None

    def __post_init__(self) -> None:
        self.extract_data_from_files()

    def extract_data_from_files(self) -> None:
        # Get path of script
        path = os.path.abspath(os.getcwd())
        
        # Get list of files in path
        files = DirHandler(path)

        # Create extractor class for evety file type
        self.pmml_data = PMMLExtractor(files.pmml_files)
        self.omdm_data = OMDMExtractor(files.model_file[0])
        self.excel_data = XlsxExtractor(files.xlsx_file[0])

    def prepare_score_card(self, card: PMMLCard) -> list[FullParam]:
        args = {}
        result = []

        for param_name in card.params:
            omdm_info = self.omdm_data.find_omdm_param(param_name)
            excel_info = self.excel_data.get_param_info(param_name)

            args["name"] = omdm_info.name
            args["_type"] = omdm_info._type
            args["pmml_name"] = param_name
            args["method"] = excel_info.method
        
            result.append(FullParam(**args))
        
        return result

    def prepare_all_cards(self) -> list[PMMLCardExt]:
        args = {}
        result = []

        for card in self.pmml_data.full_pmml_data:
            args["score_name"] = card.score_name
            args["params"] = self.prepare_score_card(card)

            result.append(PMMLCardExt(**args))
        
        return result
