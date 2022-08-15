import os
from dataclasses import dataclass, field

from src.settings import get_logger
from src.data_classes import Files


log = get_logger("dir_handler.log")


@dataclass
class DirHandler():

    path: str
    xlsx_file: str = ""
    model_file: str = ""
    pmml_files: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.path:
            log.fatal("Empty path!")
            raise SystemExit
        else:
            self.xlsx_file = self.get_sorted_files()["xlsx"]
            self.model_file = self.get_sorted_files()["txt"]
            self.pmml_files = self.get_sorted_files()["pmml"]

    def get_dir_list(self) -> list:

        exception = "requirements.txt"

        try:
            listdir = os.listdir(self.path)
        except Exception as e:
            log.fatal(e)

        if exception in listdir:
            listdir.remove(exception)

        return listdir

    def get_files_with_extension(self, extension: str) -> list:
        """
        Return list with full file names:
        ['test.pmml', 'test2.pmml']
        """

        result = []

        for _file in self.get_dir_list():
            f = os.path.splitext(_file)
            if f[1] == extension:
                result.append(f"{f[0]}{f[1]}")

        return result

    def get_sorted_files(self) -> Files:
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

        return files
