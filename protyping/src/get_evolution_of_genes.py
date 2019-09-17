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
from module.genesParsing import *


def main():
  """
    Example of call:
    ./get_evolution_of_genes.py
    It will launch script using default paths, stored in ./src/configuration_evolution_genes.ini
    If script is launched using arguments here is the documentation to use them:
    usage: get_evolution_of_genes.py [-h] [-c [CORGIPATH]] [-o [OUTPUTPATH]]
                                   [-g [GENETEMPLATE]]

    optional arguments:
      -h, --help            show this help message and exit
      -c [CORGIPATH], --corgiPath [CORGIPATH]
                            Give a path to access to CoRGI output file
      -o [OUTPUTPATH], --outputPath [OUTPUTPATH]
                            Give a path to output JSON file
      -g [GENETEMPLATE], --geneTemplate [GENETEMPLATE]
                            Give a path to gene tempalte JSON file

    Goal of this script is to consctruct a JSON file gathering data to construct all graphs representing evolution of GO term and associated genes throught time.
    Input files are list of Gene ID (ATG) represented in CoRGI at each iterations of CoRGI's algorithm. Output file is a JSON file as following sample.
    {"graph":{
      "molecular_function":{
        "nodes":[
          { "mappedData": […],
            "lbl": "cytoskeleton",
            "type": "CLASS",
            "meta": {…},
            "iteration": "2",
            "id": "2#GO:0005856",
            "relativeValue": 7.292,
          },
        ],
        "links":[
          {
            "source":"2#GO:0005856","target":"1#GO:0005856","pred":"is_a", "value":1, "iteration":1
          }
        ]
      },
      "biological_process":{...},
      "cellular_component":{...},
      }
      "iteration":{
      'iteration_0': 434,
      'iteration_1': 264,
      'iteration_2': 96,
      'iteration_3': 37}
    }

    Graph key gather all graph in node-link fashion, iteration key gather number of mappedExperiments for each iteration
  """


  #############################################################################
  # Load configuration and arguments
  #############################################################################
  # Load config file
  config = loadConfig('.../conf/configuration_evolution_genes.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getGenesArguments(config)


  #############################################################################
  # Load files
  #############################################################################
  # Load gene Informations file as a Json object
  geneInformationsJson = openJsonFile(config["default_settings"]
                                      ["geneInformationsPath"])
  # Load a template of nodes of GO slim's stored in JSON format. Contains all nodes at the lowest level of detail of the GO slim
  geneTemplate = openJsonFile(args.geneTemplate)
  geneTemplate = prepareGeneTemplate(geneTemplate)
  # Load CoRGI iterations
  resultsParsingCorgiOutput = parseCorgiOutput(args.corgiPath)
  # Parse results, and get only genes informations throught time
  corgiGenes = resultsParsingCorgiOutput[1]


  #############################################################################
  # Construct JSON for visualization
  #############################################################################
  metadataWholeJson = {
    "graph": {},
    "iteration": '',
    "sizeOfGOPart":{
      "cellular_component":{},
      "molecular_function":{},
      "biological_process":{}
    },
    "inputDataset":{
      "total":0,
      "cellular_component":{},
      "molecular_function":{},
      "biological_process":{}
    }
  }
  # Determine how many iterations CoRGI has done
  metadataWholeJson["iteration"] = getSizeOfIterations(corgiGenes)
  # Save namespace in an array
  namespace = ["cellular_component",
               "molecular_function", "biological_process"]
  # Loop on three part of GO (molecular_function, cellular_component, biological_process)
  for name in namespace:
    # Create all nodes with a unique ID in right GOSlim part and an iteration number
    metadataWholeJson["graph"][name] = createGeneNodes(geneTemplate[name], metadataWholeJson["iteration"])
    # Add enrichied genes from CoRGI output of each iteration in right GOSlim term. Delete all nodes without mapped genes in it.
    metadataWholeJson["graph"][name] = mapOnGeneNodes(
        corgiGenes, geneInformationsJson, metadataWholeJson["iteration"], metadataWholeJson["graph"][name])
    # For each part of GO calculate how many genes are mapped on each GOSlim term at each iterations.
    getSizeOfGOParts(metadataWholeJson["sizeOfGOPart"], metadataWholeJson["graph"][name])
    # Calculate a relative value for each node based on number of genes mapped on it and total of genes in current iteration
    addRelativeValueForGOParts(metadataWholeJson["sizeOfGOPart"], metadataWholeJson["graph"][name], name)
    # Add all existing edges between previously created nodes
    addEdges(metadataWholeJson["graph"][name])
    # Get all node from input allowing to carry out fisher test between a given iteration and input
    getAllNodesFromInput(metadataWholeJson["graph"][name],metadataWholeJson["inputDataset"])
  # Output Json object into a Json minified file
  saveJsonFile(config["default_settings"]
               ["genesJsonOutputPath"], metadataWholeJson)

# Execution of algorithm
main()
