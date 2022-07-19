import os
import logging as log
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import pandas

from src.data_classes import Param, Files, PMMLCard
from src.settings import get_logger



# Logger settings
#==================================================================================
log = get_logger("script.log")







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
