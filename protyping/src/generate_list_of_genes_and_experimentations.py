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


def main():

  #############################################################################
  # Load configuration and arguments
  #############################################################################
  # Load config file
  config = loadConfig('../conf/generate_list_of_genes_and_experimentations.ini')
  # Load CoRGI iterations
  resultsParsingCorgiOutput = parseCorgiOutput(
      config["default_settings"]["corgiOutput"])
  # Parse CoRGI results
  corgiOuput = {}
  corgiOuput["experimentations"] = resultsParsingCorgiOutput[0]
  corgiOuput["genes"] = resultsParsingCorgiOutput[1]
  saveJsonFile(config["default_settings"]["jsonOutputPath"], corgiOuput)


main()
