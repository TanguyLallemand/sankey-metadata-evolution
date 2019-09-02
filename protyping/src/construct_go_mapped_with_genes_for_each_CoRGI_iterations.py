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
from module.genesParsing import *


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
  file. To finish, it map genes from TAIR database on Gene Ontology and save it in a global Json This last step is Parallelized to use all cpu cores available

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
  config = loadConfig('./conf/construct_go_mapped_with_genes_for_each_CoRGI_iterations.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getCompleteGOThroughTimeArguments(config)

  GOJson = openJsonFile(args.GOpath)
  geneInformationsJson = openJsonFile(config["default_settings"]["geneInformationsPath"])
  # Load CoRGI iterations
  resultsParsingCorgiOutput = parseCorgiOutput(args.corgiPath)
  # Parse results, and get only genes informations throught time
  corgiGenes = resultsParsingCorgiOutput[1]


  #############################################################################
  # Map genes on Gene Ontology slim and calculate weight of each nodes.
  # Save it in a global Json
  #############################################################################
  # Delete useless informations from every nodes storing meta informations such as known, synonyms
  GOJson = deleteUselessInformations(GOJson)
  print("Map genes on Gene Ontology and calculate weight of each nodes.  Save it in a global Json")
  for i in range(0,len(corgiGenes)):
    GOJson = mapOnGeneNodesCompleteGO(corgiGenes["iteration_"+str(i)], geneInformationsJson, GOJson)
    # Calculate weight of each edges
    # GOJson = calculateEdgesValues(GOJson)
    # Output Json object into a Json minified file
    saveJsonFile(config["default_settings"]["globalJsonOutputPath"]+"_iteration_"+str(i)+".json", GOJson)

# Execution of algorithm
main()
