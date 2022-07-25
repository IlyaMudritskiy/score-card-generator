from dataclasses import dataclass, field
import xml.etree.ElementTree as ET

import pandas

from data_classes import OMDMParam, FullParam, PMMLCard,ExcelParam, Files
from settings import get_logger


log = get_logger("params_handler.log")


@dataclass
class PMMLExtractor:

    pmml_files: list = field(default_factory=list)
    full_pmml_data: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.pmml_files:
            log.fatal("No '.pmml' files!")
            raise SystemExit
        else:
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

    def parse_all_pmml(self) -> None:
        """
        Parse ALL pmml files!

        Return list of PMMLCard classes
        """
        all_pmml_data = []

        for pmml_file in self.pmml_files:
            all_pmml_data.append(self.get_pmml_data(pmml_file))

        return all_pmml_data

# TODO - Переписать класс, чтобы файл парсился один раз, а после происходил поиск данных
@dataclass
class OMDMExtractor:

    model_file: str

    def __post_init__(self) -> None:
        if not self.model_file:
            log.fatal("No 'model.txt' file!")
            raise SystemExit

    def get_omdm_params(self) -> dict:

        """
        Return list of OMDMParam class instances:
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


@dataclass
class XlsxExtractor:

    filename: str
    sheet: pandas.DataFrame = pandas.DataFrame()

    def __post_init__(self):
        self.sheet = self.parse_xlsx()

    def parse_xlsx(self) -> pandas.DataFrame:
        """Return a DataFrame object with excel sheet content."""

        try:
            xlsx_sheet = pandas.read_excel(self.filename, sheet_name='Data')
            log.debug(f"OK - File '{self.filename}' was parsed into dataframe.")

        except Exception as e:
            log.error(e)

        return xlsx_sheet

    def find_param_in_xlsx(self, param: str) -> pandas.DataFrame:
        """Return a DataFrame object with all occurances of inputed param."""

        param_query = [param.upper(), param.lower(), param]

        try:
            result = self.sheet.loc[self.sheet['Var_Name'].isin(param_query)]
            
        except Exception as e:
            log.error(e)

        return result

    def get_param_info(self, param_name: str) -> None:
        """Return ExcelParam instance with name and method from all occurances in excel."""

        param_info = {}

        try:
            excel_info = self.find_param_in_xlsx(param_name).to_dict()
        except Exception as e:
            log.error(e)

        var_name = list(excel_info["Var_Name"].values())
        var_methods = list(excel_info["OMDM Data_Method"].values())

        # Check if "Var_Name" is empty
        if not var_name:
            log.error(f"Parameter {param_name} was not found.")

        if var_name:
            param_info["name"] = list(dict.fromkeys(var_name))
            param_info["method"] = list(dict.fromkeys(var_methods))

        return ExcelParam(**param_info)




@dataclass
class ParamsCombiner:

    score_card: PMMLCard
    omdm: list = field(default_factory=list)
    excel: list = field(default_factory=list)



    def get_full_param_list():
        ...

def main():
    xl = XlsxExtractor("test.xlsx")
    param = input("Param >>>")
    res = xl.find_param_in_xlsx(param)
    print(res)
    p = xl.get_param_info(param)
    print(p)

if __name__ == "__main__":
    main()