import os
import logging as log
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import pandas

from src.data_classes import Param, Files, PMMLCard

# Basic settings
#==================================================================================
PATH = "C:\Programming\excel-xml"

# Logger settings
#==================================================================================
FORMAT = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
log.basicConfig(level=log.DEBUG,
                format=FORMAT,
                filename='./script.log',
                filemode='a')


class DirHandler():

    def __init__(self, path: str) -> None:
        if not path:
            log.fatal("Empty path!")
            raise SystemExit
        self.path = path

    def get_dir_list(self) -> list:

        try:
            return os.listdir(self.path)
        except Exception as e:
            log.fatal(e)

    def get_files_with_extension(self, extension: str) -> list:

        """
        Return list with full file names:
        ['test.pmml', 'test2.pmml']
        """

        result = []

        for _file in self.get_dir_list():
            _f = os.path.splitext(_file)
            if _f[1] == extension:
                result.append(f"{_f[0]}{_f[1]}")

        log.debug(f"OK - list of files with '{extension}' extension created")
        return result

    def get_sorted_files(self) -> dict:

        """
        Return object Files {
            'xlsx': 'test.xlsx', 
            'pmml': ['test.pmml', 'test2.pmml'], 
            'txt': 'model.txt'
            }
        """

        files = {}

        files["xlsx"] = self.get_files_with_extension(".xlsx")
        files["pmml"] = self.get_files_with_extension(".pmml")
        files["txt"] = self.get_files_with_extension(".txt")

        result = Files(**files)

        log.debug(f"OK - List with sorted files was created")
        return result


class PMML:

    def __init__(self, pmml_files: list) -> None:
        if not pmml_files:
            log.fatal("No '.pmml' files!")
            raise SystemExit
        else:
            self.pmml_files = pmml_files

    def get_pmml_data(self, filename: str) -> PMMLCard:
        
        """
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
            log.debug(f"OK - PMML file '{filename}' parsed.")
        except Exception as e:
            log.error(e)
        
        result = PMMLCard(score_name, params)

        return result


class OMDM:

    def __init__(self, model_file: list, xlsx_file: str) -> None:

        if not model_file:
            log.fatal("No 'model.txt' file!")
            raise SystemExit

        if not xlsx_file:
            log.fatal("No '.xlsx' file!")
            raise SystemExit

        else:
            self.model_file = model_file
            self.xlsx_file = xlsx_file

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
                p = Param(**_)
                result.append(p)

            log.debug(f"OK - Model '{self.model_file}' parsed.")

        except Exception as e:
            log.error(e)

        return result

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
class OMDMCode:

    param: str
    _type: str
    method: str
    omdm_logic: str = ""
    omdm_logging: str = ""

    def __post_init__(self):
        self.set_omdm_logic()
        self.set_omdm_logging()
    
    def set_omdm_logic(self) -> None:
        if self._type == "decimal":
            result = (
                f'xScoreInput.{self.param} := dmi_App_Get_ScoreVariableValue("#{self.param}");\n'
                f'if(xScoreInput.{self.param} = -99999) then\n'
                f'    xScoreInput.{self.param} = {self.method};\n'
                f'endif'
            )
        if self._type == "string":
            result = (
                f'xScoreInput.{self.param} := dms_App_Get_NumToStr(dmi_App_Get_ScoreVariableValue("#{self.param}"));\n'
                f'if(xScoreInput.{self.param} = "-99999") then\n'
                f'    xScoreInput.{self.param} = dms_App_Get_NumToStr({self.method});\n'
                f'endif'
            )
        self.omdm_logic = result
        

    def set_omdm_logging(self) -> None:
        if self._type == "decimal":
            result = f'dmw_App_AddScoreCardVariablesParam2CDA("{self.param}", xScoreInput.{self.param});\n'
        if self._type == "string":
            result = f'dmw_App_AddScoreCardVariablesParam2CDA("{self.param}", Val(xScoreInput.{self.param}));\n'
        self.omdm_logging = result
        

@dataclass
class BLAZECode:

    pmml_param_name: str
    omdm_param_name: str
    score_card_name: str
    _type: str
    first_lines: str = ""
    params_lines: str = ""
    end_lines: str = ""

    def set_first_lines(self) -> None:
        result = (
            f'if theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.SCORECARDNAME = "{self.score_card_name}" then\n'
            '{\n'
            f'\t_{self.score_card_name}In is a {self.score_card_name}In;\n'
        )
        self.first_lines = result

    def set_end_lines(self):
        result = (
            f'_{self.score_card_name}Out is some {self.score_card_name}Out initially {self.score_card_name}(_{self.score_card_name}In);\n'
            f'score = _{self.score_card_name}Out.score;\n'
            f'label = _{self.score_card_name}Out.label;\n'
            '}\n'
        )
        self.end_lines = result

    def set_params_lines():
        ...





def main():
    args = {
      "param": "AGE",
      "_type": "decimal",
      "method": "dm_Get_Age"
    }

    oc = OMDMCode(**args)
    print(oc.omdm_logic)
    print(oc.omdm_logging)

if __name__ == "__main__":
    main()
