from dataclasses import dataclass
from settings import get_logger

log = get_logger("code_generators.log")


@dataclass
class OMDMCode:

    param: str
    _type: str
    method: str
    omdm_logic: str = ""
    omdm_logging: str = ""

    def __post_init__(self):
        # Fill class properties with ready code on creation
        self.set_omdm_logic()
        self.set_omdm_logging()
    
    def set_omdm_logic(self) -> None:
        # OMDM code for decimal params
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
        # Set the beginning of code
        result = (
            f'if theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.SCORECARDNAME = "{self.score_card_name}" then\n'
            '{\n'
            f'\t_{self.score_card_name}In is a {self.score_card_name}In;\n'
        )
        self.first_lines = result

    def set_params_lines(self) -> None:
        # Set the middle part of code
        if self._type == "decimal":
            result = (
                f"_{self.score_card_name}In.{self.pmml_param_name} = theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.{self.omdm_param_name};\n"
            )
        if self._type == "string":
            result = (
                f"_{self.score_card_name}In.{self.pmml_param_name} = portable().toInteger(theApp.CDA_NdScoreModel.Cda_NdScoreModelInputInfo.{self.omdm_param_name};\n"
            )
        self.params_lines = result

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
class ReportFields:

    score_card_name: str
    params: list
    report_fields: list = []

    def get_report_field(self, param: str) -> None:
        result = f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore/CDAScoreParam[@CDASPNAME='{param}']/@CDASPVALUE"
        return result

    def set_fields(self) -> None:
        start = (
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/@CDASCRNAME\n"
            f"/Application/CDA[@CDAISACTIVE='Active']/@CDADATE\n"
            f"/Application/ServiceCall/SCBurRes/SCSINGLE_FORMAT/@SCSFGROUPID\n"
        )
        end = (
            f"/Application/ApplicationScoring/ScoreModelOutput[@ScoreModelName='{self.score_card_name}']/@FinalScore\n"
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Prediction_proba']/@CDASPVALUE\n"
            f"/Application/CDA[@CDAISACTIVE='Active']/CDAScore[@CDASCRNAME='{self.score_card_name}']/CDAScoreParam[@CDASPNAME='Calibrated_Score']/@CDASPVALUE\n"
        )

        self.report_fields.append(start)

        for param in self.params:
            line = self.get_report_field(param)
            self.report_fields.append(line)

        self.report_fields.append(end)
