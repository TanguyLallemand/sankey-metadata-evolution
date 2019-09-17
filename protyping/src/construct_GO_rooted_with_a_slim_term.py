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
from module.constructGOrooted import *

from joblib import Parallel, delayed
import multiprocessing

def main():
  """
  Example of launch call:
  ./construct_GO_rooted_with_a_slim_term.py
  It will launch script using default paths, stored in ./src/./construct_GO_rooted_with_a_slim_term.ini
  If script is launched using arguments here is the documentation to use them:

  usage: construct_GO_rooted_with_a_slim_term.py [-h] [-g [GOFILE]]
                                               [-t [GENETEMPLATE]]

  optional arguments:
    -h, --help            show this help message and exit
    -g [GOFILE], --GOfile [GOFILE]
                          Give a path to GO json file with mapped genes
    -t [GENETEMPLATE], --geneTemplate [GENETEMPLATE]
                          Give a path to gene template JSON file gathering GO
                          slim terms

  This function aims to build a set of Json files containing the part of the GO below a slim GO node. The genes involved are mapped to their GO term. The product files are named by the GO ID of the Go Slim term
  """


  ##############################################################################
  # Load configuration and arguments
  ##############################################################################
  # Load config file
  config = loadConfig('../conf/construct_GO_rooted_with_a_slim_term.ini')
  # Load arguments, if no argument are given when call this script, config informations are used
  args = getGOSlimRootedArguments(config)
  # Get number of available cores
  num_cores = multiprocessing.cpu_count()


  ##############################################################################
  # Construct all GO rooted by a go slim term
  ##############################################################################

  # Load Json file given in parameter
  GOSlimNodes = openJsonFile(args.geneTemplate)
  goIDarray=[]
  # Get all GO ID of GO slim terms
  getGOIDOfGOSlimTerms(GOSlimNodes, goIDarray)
  print("Construction of "+ str(len(goIDarray)) + " files")
  for i in range(0,5):
    # Load Json file given in parameter
    GOfile = openJsonFile(args.GOfile+str(i)+".json")
    # Using a parallelized fashion, for each GO ID of Go slim terms get all nodes and links under current go slim term
    Parallel(n_jobs=num_cores)(delayed(initializeComputation)([GOID], GOfile,i) for GOID in goIDarray)

main()
