import os
import logging as log
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import pandas

from src.data_classes import Param, Files, PMMLCard
from settings import get_logger

# Basic settings
#==================================================================================
PATH = "C:\Programming\excel-xml"

# Logger settings
#==================================================================================
log = get_logger("script.log")


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
