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
from module.generalParsing import *
from module.ontologyParsing import *



def main():
  """
  Example of launch call:
  ./get_tair_ontologies.py
  It will launch script using default paths, stored in ./src/configuration_tair.ini
  If script is launched using arguments here is the documentation to use them:

  usage: get_tair_ontologies.py [-h] [-p [GOPATH]] [-u [URL]] [-t [TYPE]]
                              [-d [DATABASE]]

  optional arguments:
    -h, --help            show this help message and exit
    -p [GOPATH], --GOpath [GOPATH]
                          Give a path to store downloaded Json from Gene
                          Ontology
    -u [URL], --url [URL]
                          Give an url in order to download an ontology in Json
                          format
    -t [TYPE], --type [TYPE]
                          Give 0 if computing a Go Slim and 1 if it is a
                          complete ontology
    -d [DATABASE], --database [DATABASE]
                          Give a path to TAIR database file, stored in TSV
                          format

  Main function of parser, three main operations are done by this script. To begin, it download and parse Json from Gene Ontology using a given URL, save result as a Json file usable for different visualisations. Following it, download and parse Json from TAIR database, using Gene ID from Corgi matrix
  file. To finish, it map genes from TAIR database on Gene Ontology and save it in a global Json.

  Returns
  -------
  Json file
      A Json file of Gene Ontology ready to view with d3.js
  Json file
      A Json file storing Gene informations of each Gene appearing in Corgi matrix. data are coming from TAIR database
  Json file
      A Json file storing Gene Ontology in nodes-edges format with mapped gene in nodes informations

  """


  #############################################################################
  # Load configuration and arguments
  #############################################################################
  # Load config file
  config = loadConfig('configuration_tair.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getTAIRArguments(config)


  #############################################################################
  # Download and parse Json from Gene Ontology
  #############################################################################
  print("Download and parse Json from Gene Ontology")
  # Execute some bash commands allowing to download Gene Ontology and execute some sed on it. This approach allow to be more efficient than parsing it using Python
  prepareJson(args)
  # Load Gene Ontology Json file as a Json object
  GOJson = openJsonFile(args.GOpath)
  # Edit ID, removing url and keeping only GO ID
  GOJson = recursiveSedInJson(GOJson, "id")
  GOJson = recursiveSedInJson(GOJson, "source")
  GOJson = recursiveSedInJson(GOJson, "target")
  # Resolve PURL of predictors
  GOJson = recursiveSedInJson(GOJson, "pred")
  # Save Downloaded GO, a temporary file in final pipeline
  saveJsonFile(args.GOpath, GOJson)


  #############################################################################
  # Download and parse Json from TAIR database, using Gene ID from Corgi matrix
  # File
  #############################################################################
  print("Download and parse Json from TAIR database")
  # Load Json file given in parameter
  jsonFile = openJsonFile(config["default_settings"]["CatmaPath"])
  with open(config["default_settings"]["listOfGeneIDPath"], mode='w+') as json_result:
    # Iterate tought local Json file, allowing to get gene product ID
    for initalJsonIterator in jsonFile:
      # Save list of gene ID in a txt file in order to get their annotations from TAIR, appear as a temporary files
      json_result.write(initalJsonIterator + '\n')
  # Get all informations for each Gene ID from a file coming from TAIR database
  tsvContent = parseTSV(config["default_settings"]["TAIRDatabase"])
  # Construct a Json object from TSV data
  geneInformationsJson = constructTAIRDatabaseJson(tsvContent)
  # Output Json object into a Json minified file
  saveJsonFile(config["default_settings"]["geneInformationsPath"], geneInformationsJson)
  # Delete useless informations from every nodes storing meta informations such as known, synonyms
  GOJson = deleteUselessInformations(GOJson)
  # Output Json object into a Json minified file
  saveJsonFile(config["default_settings"]["globalJsonOutputPath"], GOJson)

# Execution of algorithm
main()
