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
from module.metadataParsing import *


def main():
  """
  Example of call:
  ./get_metadata.py
  It will launch script using default paths, stored in ./src/configuration_metadata.ini
  If script is launched using arguments here is the documentation to use them:

    usage: get_metadata.py [-h] [-p [METADATAPATH]] [-t [METADATATEMPLATE]]
                         [-c [CORGIPATH]] [-o [OUTPUTPATH]]

    optional arguments:
      -h, --help            show this help message and exit
      -p [METADATAPATH], --metadataPath [METADATAPATH]
                            Give a path to access to metadata file
      -t [METADATATEMPLATE], --metadataTemplate [METADATATEMPLATE]
                            Give a path to access to a template of metadata file
                            needed by d3.js
      -c [CORGIPATH], --corgiPath [CORGIPATH]
                            Give a path to access to CoRGI output file
      -o [OUTPUTPATH], --outputPath [OUTPUTPATH]
                            Give a path to output JSON file


  Goal of this script is to consctruct a JSON file gathering data to construct all graphs representing evolution of experiment's metadata throught time.
  Input files are list of experiments represented in CoRGI and ID of experiments represented at each iterations of CoRGI's algorithm. Output file is a JSON file as following sample.
  {
  "graph":{
    "cond1":{
      "nodes":[
        {
          "id":"0#3.1",
          "cond":"cond3",
          "mappedData":[
            "0#0#1338": {
              "cond1": "",
              "cond2": ["2.2"],
              "cond3": ["1"],
              "cond4": "0",
              "control": "stem_2",
              "experiment": "stem developement",
              "keywords": "10cm/2cm",
              "link": "http://tools.ips2.u-psud.fr/cgi-bin/projects/CATdb/consult_expce.pl?experiment_id=0#1338",
              "projet": "AF09_lignin",
              "swap": "stem_10 / stem_2",
              "treatment": "stem_10",
              "type": "microarray",
              "warning": ""
            },
          ],
          "class":"stress",
          "lbl":"Development",
          "iteration":0
        },
      ],
      "links":[
        {
          "source":"0#3.1",
          "target":"0#3.2",
          "pred":"is_a",
          "value":1,
          "iteration":0
        }
      ]
    },
    "cond2":{...},
    "cond3":{...},
    "cond4":{...},
    }
    "iteration":{
      "iteration_0": 1042,
      "iteration_1": 35,
      "iteration_2": 19,
      "iteration_3": 10
    }
  }

  Graph key gather all graph in node-link fashion, iteration key gather number of mappedExperiments for each iteration
    """

  #############################################################################
  # Load configuration and arguments
  #############################################################################
  # Load config file
  config = loadConfig('./conf/configuration_metadata.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getMetadataArguments(config)


  #############################################################################
  # Load files
  #############################################################################
  # Load Metadata Json file as a Json object
  catmaMetadataJson = openJsonFile(args.metadataPath)
  # Load a template of metadata stored in JSON format. Contains all possible metadata and associated informations
  metadataTemplate = openJsonFile(args.metadataTemplate)
  # Load CoRGI iterations
  resultsParsingCorgiOutput = parseCorgiOutput(args.corgiPath)
  # Parse results
  corgiExperiments = resultsParsingCorgiOutput[0]


  #############################################################################
  # Construct JSON for visualization
  #############################################################################
  metadataWholeJson = {
    "graph":{},
    "iteration":'',
    "sizeOfCategoryPart":{
      "cond1":{},
      "cond2":{},
      "cond3":{},
      "cond4":{}
    },
    "inputDataset":{
      "total":0,
      "cond1":{},
      "cond2":{},
      "cond3":{},
      "cond4":{}
    }
  }
  # Determine how many iterations CoRGI has done and count of experiments for each of them
  metadataWholeJson["iteration"] = getSizeOfIterations(corgiExperiments)
  # Loop on four possible conditions (cond1,cond2,cond3,cond4)
  for condition in range(1,5):
    metadataWholeJson["graph"]["cond" + str(condition)] = {"nodes":[], "links":[]}
    # Create all nodes
    metadataWholeJson["graph"]["cond" + str(condition)] = createMetadataNodes(corgiExperiments, catmaMetadataJson, metadataTemplate, metadataWholeJson["sizeOfCategoryPart"], condition, metadataWholeJson["graph"]["cond" + str(condition)])
    getSizeOfCategoryPart(metadataWholeJson["graph"]["cond" + str(condition)],metadataWholeJson["sizeOfCategoryPart"])
    # Calculate node relative value. (percentage of representation of a particular conditions relatively to all experiments of a given iteration)
    calculateNodesValues(metadataWholeJson["graph"]["cond" + str(condition)], metadataWholeJson["iteration"])
    # Add all existing edges between previously created nodes
    addEdges(metadataWholeJson["graph"]["cond" + str(condition)])
    # Get all node from input allowing to carry out fisher test between a given iteration and input
    getAllNodesFromInput(metadataWholeJson["graph"]["cond" + str(condition)],metadataWholeJson["inputDataset"])
  # Output Json object into a Json minified file
  saveJsonFile(config["default_settings"]
               ["metadataJsonOutputPath"], metadataWholeJson)

# Execution of algorithm
main()
