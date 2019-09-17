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

from module.importExportData import *


def initializeComputation(goIDarray, GOfile,iteration):
  GOSlimrooted = {
      "nodes": [],
      "links": []
  }
  getAllChildren(goIDarray, GOfile, GOSlimrooted)
  print("Saving ../data/output/GORooted/" + str(iteration)+"_"+goIDarray[0] + ".json")
  # Output Json object into a Json minified file
  saveJsonFile("../data/output/GORooted/" + str(iteration)+"_"+ goIDarray[0] + ".json", GOSlimrooted)


def getGOIDOfGOSlimTerms(goSlimJson, goIDarray):
  for nodes in goSlimJson["nodes"]:
    goIDarray.append(nodes["id"])


def getNodesFromGOID(GOID, GO):
  for nodes in GO:
    if nodes["id"] == GOID:
      return nodes
  return None


def getAllChildren(goIDarray, GOfile, GOSlimrooted):
  addedNodes = []
  for GOID in goIDarray:
    for links in GOfile["edges"]:
      if links["target"] == GOID:
        GONodeSource = getNodesFromGOID(links["source"], GOfile["nodes"])
        GONodeTarget = getNodesFromGOID(links["target"], GOfile["nodes"])
        if GONodeTarget is not None:
          GOSlimrooted["nodes"].append(GONodeTarget)
          GOfile["nodes"].remove(GONodeTarget)
        if GONodeSource is not None:
          GOSlimrooted["nodes"].append(GONodeSource)
          if GONodeSource["id"] not in addedNodes:
            addedNodes.append(GONodeSource["id"])
          GOfile["nodes"].remove(GONodeSource)

        GOSlimrooted["links"].append(links)
        GOfile["edges"].remove(links)
  if len(addedNodes) != 0:
    getAllChildren(addedNodes, GOfile, GOSlimrooted)
  else:
    return 0
