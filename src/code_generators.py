from dataclasses import dataclass, field
import os

from src.settings import get_logger
from src.data_classes import FullParam, PMMLCardExt

log = get_logger("code_generators.log")


@dataclass
class CodeMixin:
    score_card_name: str = field(default_factory=str)
    params: list[FullParam] = field(default_factory=list)
    code: list = field(default_factory=list)


@dataclass
class OMDMCode(CodeMixin):

    def __post_init__(self) -> None:
        # Fill class properties with ready code on creation
        self.set_omdm_code()

    def get_logic_code(self, param: FullParam) -> list[str]:
        if param._type == "decimal":
            result = [
                f'xScoreInput.{param.name} := dmi_App_Get_ScoreVariableValue("#{param.name}");\n',
                f'if(xScoreInput.{param.name} = -99999) then\n',
                f'    xScoreInput.{param.name} = {param.method};\n',
                f'endif\n',
            ]
        
        if param._type == "string":
            result = [
                f'xScoreInput.{param.name} := dms_App_Get_NumToStr(dmi_App_Get_ScoreVariableValue("#{param.name}"));\n',
                f'if(xScoreInput.{param.name} = "-99999") then\n',
                f'    xScoreInput.{param.name} = dms_App_Get_NumToStr({param.method});\n',
                f'endif\n',
            ]
        
        return result

    def get_logging_code(self, param: FullParam) -> list[str]:
        if param._type == "decimal":
            result = [f'dmw_App_AddScoreCardVariablesParam2CDA("{param.name}", xScoreInput.{param.name});\n',]

        if param._type == "string":
            result = [f'dmw_App_AddScoreCardVariablesParam2CDA("{param.name}", Val(xScoreInput.{param.name}));\n',]

        return result

    def get_omdm_logic(self) -> list[str]:
        result = []

        for param in self.params:
            result += self.get_logic_code(param=param)

        return result

    def get_omdm_logging(self) -> list[str]:
        result = []

        for param in self.params:
            result += self.get_logging_code(param=param)

        return result

    def set_omdm_code(self) -> None:
        self.code += self.get_omdm_logic()
        self.code += "\n"
        self.code += self.get_omdm_logging()


@dataclass
class BLAZECode(CodeMixin):

    def __post_init__(self):
        self.set_blaze_code()

    def get_first_lines(self) -> list[str]:
        # Get the beginning of code
        result = [
            f'if theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.SCORECARDNAME = "{self.score_card_name}" then\n',
            '{\n',
            f'\t_{self.score_card_name}In is a {self.score_card_name}In;\n',
        ]
        
        return result

    def get_param_line(self, param: FullParam) -> list[str]:
        # Get a line for param
        if param._type == "decimal":
            result = [
                f"\t_{self.score_card_name}In.{param.pmml_name} = theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.{param.name};\n",
            ]

        if param._type == "string":
            result = [
                f"\t_{self.score_card_name}In.{param.pmml_name} = portable().toInteger(theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.{param.name});\n",
            ]

        return result

    def get_params_lines(self) -> list[str]:
        result = []

        for param in self.params:
            result += self.get_param_line(param)
        
        return result

    def get_last_lines(self) -> list[str]:
        result = [
            f'\t_{self.score_card_name}Out is some {self.score_card_name}Out initially {self.score_card_name}(_{self.score_card_name}In);\n',
            f'\tscore = _{self.score_card_name}Out.score;\n',
            f'\tlabel = _{self.score_card_name}Out.label;\n',
            '}\n',
        ]

        return result

    def get_blaze_code(self):
        result = []

        result += self.get_first_lines()
        result += self.get_params_lines()
        result += self.get_last_lines()

        return result

    def set_blaze_code(self) -> None:
        self.code = self.get_blaze_code()


    def set_end_lines(self) -> None:
        # Set the end of code
        result = (
            f'_{self.score_card_name}Out is some {self.score_card_name}Out initially {self.score_card_name}(_{self.score_card_name}In);\n'
            f'score = _{self.score_card_name}Out.score;\n'
            f'label = _{self.score_card_name}Out.label;\n'
            '}\n'
        )
        self.end_lines = result


@dataclass
class ReportFields(CodeMixin):

    fields_type: str = field(default_factory=str)
    start: int = 0

    def __post_init__(self):
        if self.fields_type == "standard":
            self.set_standard_report()

        if self.fields_type == "advanced":
            self.set_advanced_report()
            self.add_counter_to_report_line()

    def add_counter_to_report_line(self) -> None:
        result = []

        for line in self.code:
            line = line + f";1;1;1;{self.start}\n"
            result.append(line)
            self.start += 1

        self.code = result

    def set_standard_report(self) -> None:

        start = [
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/@CDASCRNAME\n",
            f"/Application/CDA[@CDAISACTIVE='Active']/@CDADATE\n",
            f"/Application/ServiceCall/SCBurRes/SCSINGLE_FORMAT/@SCSFGROUPID\n",
        ]

        self.code += start

        for param in self.params:
            self.code.append(f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore/CDAScoreParam[@CDASPNAME='{param.name}']/@CDASPVALUE\n")
            
        end = [
            f"/Application/ApplicationScoring/ScoreModelOutput[@ScoreModelName='{self.score_card_name}']/@FinalScore\n",
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Prediction_proba']/@CDASPVALUE\n",
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Calibrated_Score']/@CDASPVALUE\n",
        ]

        self.code += end

    def set_advanced_report(self) -> None:

        start = [
            f"\#ScoreCard=/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/@CDASCRNAME",
            f"\#CDADATE=/Application/CDA[@CDAISACTIVE='Active']/@CDADATE",
            f"\#SCSFGROUPID=/Application/ServiceCall/SCBurRes/SCSINGLE_FORMAT/@SCSFGROUPID",
        ]

        self.code += start

        for param in self.params:
            self.code.append(f"\#{param.name}=/Application/CDA[@CDAISACTIVE='Active']/CDAScore/CDAScoreParam[@CDASPNAME='{param.name}']/@CDASPVALUE")
            
        end = [
            f"\#FinalScore=/Application/ApplicationScoring/ScoreModelOutput[@ScoreModelName='{self.score_card_name}']/@FinalScore",
            f"\#CDASPVALUE/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Prediction_proba']/@CDASPVALUE",
            f"\#CDASPVALUE/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Calibrated_Score']/@CDASPVALUE",
        ]

        self.code += end


@dataclass
class CodeCombiner():

    score_card_list: list[PMMLCardExt] = field(default_factory=list)

    def get_code_for_card(self, card: PMMLCardExt) -> dict:
        result = {}

        result["omdm"] = OMDMCode(card.score_name, card.params)
        result["blaze"] = BLAZECode(card.score_name, card.params)
        result["report"] = ReportFields(card.score_name, card.params, fields_type="standard")

        return result

    def get_code_for_all_cards(self) -> list[list]:
        result = []
        for card_ext in self.score_card_list:
            result.append([card_ext.score_name ,self.get_code_for_card(card_ext)])

        return result


def main():

    """
    To test the code examples run this file.
    """

    # Set the params
    full_param_1 = {
        "name": "Age",
        "_type": "decimal",
        "pmml_name": "AGE",
        "method": "dmi_App_Get_AGE",
    }
    fp1 = FullParam(**full_param_1)

    full_param_2 = {
        "name": "Gender",
        "_type": "string",
        "pmml_name": "GENDER",
        "method": "dmi_App_Get_GENDER",
    }
    fp2 = FullParam(**full_param_2)

    params = [fp1, fp2]

    # OMDM Code
    oc = OMDMCode(params=params)
    with open("code_examples/omdm_example.md", "w") as f:
        f.write("```js\n")
        for line in oc.code:
            f.write(line)
        f.write("```\n")

    # Blaze Code
    blaze_params = {
        "score_card_name": "INC22_IL_HIT_S",
        "params": params,
    }

    bc = BLAZECode(**blaze_params)
    with open("code_examples/blaze_example.md", "w") as f:
        f.write("```js\n")
        for line in bc.code:
            f.write(line)
        f.write("```\n")

    # Report fields
    # Standard report fields to put into NSTM directly
    p_standard = {
        "fields_type": "standard", 
        "score_card_name": "INC22_IL_HIT_S", 
        "params": params, 
        "start": 73
    }
    rf_st = ReportFields(**p_standard)
    with open("code_examples/report_fields_standard.md", "w") as f:
        f.write("```js\n")
        for line in rf_st.code:
            f.write(line)
        f.write("```\n")

    # Advanced report fields to put into NSTM config file
    p_advanced = {
        "fields_type": "advanced", 
        "score_card_name": "INC22_IL_HIT_S", 
        "params": params, 
        "start": 73
    }
    rf_adv = ReportFields(**p_advanced)
    with open("code_examples/report_fields_advanced.md", "w") as f:
        f.write("```js\n")
        for line in rf_adv.code:
            f.write(line)
        f.write("```\n")

if __name__ == "__main__":
    main()
