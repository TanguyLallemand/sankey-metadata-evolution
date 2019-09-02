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
from module.constructionOfFisherDb import *
from module.importExportData import *
from module.generalParsing import getSizeOfIterations

def main():
  """
  Example of launch call:
  ./fisher_dataset.py
  It will launch script using default paths, stored in ./src/configuration_fisher_dataset.ini
  If script is launched using arguments here is the documentation to use them:

  usage: fisher_dataset.py [-h] [-d [DATABASE]] [-c [CORGIPATH]]
                         [-p [METADATAPATH]] [-t [METADATATEMPLATE]]

  optional arguments:
    -h, --help            show this help message and exit
    -d [DATABASE], --database [DATABASE]
                          Give a path to TAIR database file, stored in TSV
                          format
    -c [CORGIPATH], --corgiPath [CORGIPATH]
                          Give a path to access to CoRGI output file
    -p [METADATAPATH], --metadataPath [METADATAPATH]
                          Give a path to access to metadata file
    -t [METADATATEMPLATE], --metadataTemplate [METADATATEMPLATE]
                          Give a path to access to a template of metadata file


  This script to count occurences of each GO Slim term in TAIR database. It also count occurences of each experiments category from CoRGI output file. These counts allows to carry out Fisher's exact test.
  """
  ##############################################################################
  # Load configuration and arguments
  ##############################################################################
  # Load config file
  config = loadConfig('./conf/configuration_fisher_dataset.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getFisherDatasetArguments(config)

  ##############################################################################
  # Parse TAIR file and CoRGI output file
  ##############################################################################
  # Load Metadata Json file as a Json object
  catmaMetadataJson = openJsonFile(args.metadataPath)
  # Load a template of metadata stored in JSON format. Contains all possible metadata and associated informations
  metadataTemplate = openJsonFile(args.metadataTemplate)
  # Get all informations for each Gene ID from a file coming from TAIR database
  tsvContent = parseTSV(config["default_settings"]["TAIRDatabase"])
  # Load CoRGI iterations
  resultsParsingCorgiOutput = parseCorgiOutput(args.corgiPath)
  # Parse results
  corgiExperiments = resultsParsingCorgiOutput[0]
  corgiGenes = resultsParsingCorgiOutput[1]
  ##############################################################################
  # Parse TAIR database, and CoRGI experiments dataset
  ##############################################################################
  TAIRDatabase = {"TAIRDb": {"total": 0}, "CoRGIExperiments": {"total": 0}, "genesIterations":'',"experimentsIterations":''}
  # Determine how many experiments there is in each CoRGI iterations
  TAIRDatabase["experimentsIterations"] = getSizeOfIterations(corgiExperiments)
  # Determine how many experiments there is in each CoRGI iterations
  TAIRDatabase["genesIterations"] = getSizeOfIterations(corgiGenes)
  # Construct a Json object from TSV data
  TAIRJson = constructTAIRDatabaseJson(tsvContent)
  # Construct a JSON that will be use to carry out Fisher exact tests
  parseTAIRDatabase(TAIRJson, TAIRDatabase["TAIRDb"])
  # Parse CoRGI experiments dataset
  parseCoRGIExperiments(catmaMetadataJson, corgiExperiments,
                        TAIRDatabase["CoRGIExperiments"], metadataTemplate)

  ##############################################################################
  # Parse TAIR database and output result in a minified Json
  ##############################################################################
  # Output Json object into a Json minified file
  saveJsonFile(config["default_settings"]["outputJson"], TAIRDatabase)


main()
