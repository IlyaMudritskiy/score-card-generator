

from src.settings import PATH
from src.dir_handler import DirHandler
from src.params_handler import ParamsCombiner, PMMLExtractor

def main() -> None:
    FullScoreCards = []

    FilesList = DirHandler(PATH)
    ScoreCards = PMMLExtractor(FilesList.pmml_files)
    for card in ScoreCards.full_pmml_data:
        full_score_card = ParamsCombiner(card)
        code_creator = CodeCreator(full_score_card)
        code_creator.create_files()