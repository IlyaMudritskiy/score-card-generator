from dataclasses import dataclass
import xml.etree.ElementTree as ET

import pandas
from accessify import private

from src.data_classes import OMDMParam, FullParam, PMMLCard, Files
from src.settings import get_logger


log = get_logger("params_handler.log")


@dataclass
class PMMLExtractor:

    pmml_files: list
    full_pmml_data: list = []

    @private
    def __post_init__(self) -> None:
        if not self.pmml_files:
            log.fatal("No '.pmml' files!")
            raise SystemExit
        else:
            # Write data parsed from ALL .pmml files to class property on creation
            self.full_pmml_data = self.parse_all_pmml()

    @private
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

    @private
    def parse_all_pmml(self) -> None:
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

    model_file: str

    def __post_init__(self) -> None:

        if not self.model_file:
            log.fatal("No 'model.txt' file!")
            raise SystemExit

        else:
            self.model_file = self.model_file

    def get_omdm_params(self) -> dict:

        """
        Return list of Param class instances:
        [
            {'name': 'param_1', 'type': 'decimal'}, 
            {'name': 'Param_2', 'type': 'decimal'}, 
            {'name': 'PARAM_3', 'type': 'string'}, 
            {'name': 'ParAm_4', 'type': 'string'}
        ]
        """

        result = []
        params_list = []

        try:
            # Open model.txt to get OMDM params
            with open(self.model_file, "r") as f:

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
                _ = {}
                _["omdm_name"] = value[0]
                # From: xs:decimal
                # To: decimal
                _["param_type"] = value[1].split(":")[1]
                p = OMDMParam(**_)
                result.append(p)

            log.debug(f"OK - Model '{self.model_file}' parsed.")

        except Exception as e:
            log.error(e)

        return result

class XlsxExtractor:

    def parse_xlsx(self, filename: str) -> pandas.DataFrame:

        """
        Return a DataFrame object with excel sheet content
        """

        try:
            xlsx_sheet = pandas.read_excel(filename, sheet_name='Data')
            log.debug(f"OK - File '{filename}' was parsed into dataframe.")

        except Exception as e:
            log.error(e)

        return xlsx_sheet

    def find_param_in_xlsx(self, sheet: pandas.DataFrame, param: str, _mode="dict") -> dict:

        """
        _mode = "dict":
            Return a dict with all occurances of required param (Non case-sensitive):
            {'Var_Name': {0: 'PARAM_1', 1: 'PARAM_1'}, 
            'Score_Card_Segment': {0: nan, 1: nan}, 
            'Score_Card_Segment_CDA': {0: nan, 1: nan}, 
            'Score_Card': { 0: nan, 1: nan}, 
            'OMDM Data_Method': {0: 'IMP_PARAM_1_1', 1: 'IMP_PARAM_1_2'}}

        _mode = "df":
            Return a DataFrame Object that can be printed in terminal
        """

        param_query = [param.upper(), param.lower(), param]

        try:
            if _mode == "dict":
                result = sheet.loc[sheet['Var_Name'].isin(param_query)].to_dict()

            if _mode == "df":
                result = sheet.loc[sheet['Var_Name'].isin(param_query)]

            log.debug(f"OK - Param '{param}' was found.")
            
        except Exception as e:
            log.error(e)

        return result


@dataclass
class ParamsCombiner:

    score_card: PMMLCard
    combined_params: FullParam = None



    def get_full_param_list():
        ...