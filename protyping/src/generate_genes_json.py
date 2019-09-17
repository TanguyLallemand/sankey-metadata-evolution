#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
################################################################################
#
#  CoRGI : The Co-Regulated Gene Investigator
#
#  Copyright: 2019 INRA http://www.inra.fr
#
#  License:
#    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#    See the LICENCE file in the project's top-level directory for details.
#
#  Author:
#    * Tanguy LALLEMAND, BIDEFI team, IRHS
#
################################################################################

import json

from module.configurationLoader import *
from module.importExportData import *
from module.generateGenesJsonLib import *

def main():
  #############################################################################
  # Load configuration and arguments
  #############################################################################
  # Load config file
  config = loadConfig('../conf/generateGenesJson.ini')
  # Load Json file given in parameter
  catmaJsonFile = openJsonFile(config["default_settings"]["CatmaPath"])
  tairDatabase = parseTSV(config["default_settings"]["TAIRDatabase"])
  constructGenesJson(catmaJsonFile,tairDatabase)
  with open(config["default_settings"]["jsonOutputPath"], mode='w+', encoding='utf-8') as outputJson:
    # Dump Json object in a file, add  indent=2, to not minify json
    json.dump(catmaJsonFile, outputJson, separators=(',', ': '), indent=2)
main()
