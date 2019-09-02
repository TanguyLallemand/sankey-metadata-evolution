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

import csv
import json

from module.generalParsing import *


def createMetadataNodes(corgiExperiments, catmaMetadataJson, metadataTemplate, sizeOfIterations, condition, metadataJson):
  """Allow to create all nodes to visualize evolution of metadata conditions. This algorithm keeps in mind the fact that data are sequential and create nodes for each iterations

  Parameters
  ----------
  corgiExperiments : Dictionnary
      Json with as keys iterations name and in value an array of all experimentation ID involved in iteration
  catmaMetadataJson : Dictionnary
      JSON gathering all informations of each experimentations. As key, ID of experimentation, as value an object of metadata
  metadataTemplate : Dictionnary
      A JSON object gathering all possible nodes. Based on Biological insight tree
  sizeOfIterations : Dictionnary
      Dictionnary with as key iteration number and as value number of experimentations involved in iteration
  condition : int
      A int from loop in main of script, allowing to select whhich condition is parsed in this function
  metadataJson : dictionnary of two arrays, one called nodes, storing all nodes of graph, and links strong all links

  Returns
  -------
  metadataJson : array
      An array containning in first cell a dictionnary of parsed experimentations with iteration number as key and as value an array of parsed metadata of experimentations. Second cell contain gene AT ID in same format as experimentations
  """
  listOfId = []
  # Iterating through experiments
  for experimentsIterator in corgiExperiments:
    # Split iteration key to get iteration number
    currentIterationNumber = experimentsIterator.split("_")[1]
    # Iterating through all ID of expermimentation for current iteration of CoRGI
    for idOfExperrimentation in corgiExperiments[experimentsIterator]:
      try:
        catmaMetadataJson[idOfExperrimentation]["cond" + str(condition)][0]
      except:
        pass
      else:
        for i in range(0,len(catmaMetadataJson[idOfExperrimentation]["cond" + str(condition)])):
          if catmaMetadataJson[idOfExperrimentation]["cond" + str(condition)][i]:
            # Construct a node ID fitting with d3.js script
            constructedId = currentIterationNumber + '#' + \
                str(condition) + "." + \
                catmaMetadataJson[idOfExperrimentation]["cond" +
                                                        str(condition)][i]
            # Check if node has not already be created because this ID was already computed
            if constructedId not in listOfId:
              # Save it in an array, allowing to keep in memory which nodes have already be computed
              listOfId.append(constructedId)
              # Create a new node, using informations from template
              templateNode = findTemplateNode(constructedId, metadataTemplate)
              # If it is not possible to create a node, create one with all gathered informations
              if templateNode == None:
                templateNode = {"id": constructedId, "mappedData": []}
              else:
                templateNode["id"] = constructedId
                templateNode["mappedData"] = []
              # Get ID of experimentation stored as a key in catma JSON file
              catmaMetadataJson[idOfExperrimentation]["experimentationID"] = idOfExperrimentation
              # Append in mappedData array all informations of each associated experiments
              templateNode["mappedData"].append(
                  catmaMetadataJson[idOfExperrimentation])
              # Append constructed node in final JSON
              metadataJson["nodes"].append(templateNode)
            # If node has already been created, just add supplementary mappedData if exist
            else:
              # Store ID of experimentation
              catmaMetadataJson[idOfExperrimentation]["experimentationID"] = idOfExperrimentation
              # Add more experiments for catma JSON
              addExperiments(catmaMetadataJson, metadataJson,
                             idOfExperrimentation, constructedId)
  return metadataJson


def findTemplateNode(constructedId, metadataTemplate):
  """Allow to construct a node object using informations gathered from CoRGI Output and also informations from metadataTemplate

  Parameters
  ----------
  constructedId : string
      A string composed by two part: first a number corresponding on iteration where node appear and in second part ID of condition represented by node. Parts are separated using '#' character
  metadataTemplate : Json Object
      A JSON object gathering all possible nodes. Based on Biological insight tree

  Returns
  -------
  templateNode : Dictionnary
      Dictionnary gathering all informations of a node. Here is an example of a node content:
      {"id":"3.3.6", "cond":"cond3", "mappedData":[],"class":"stress", "lbl":"Light (UV...)", "relativeValue":41},
  """
  # Split contructed ID using '#' character
  nodeSplitted = constructedId.split('#')
  # Iterate through nodes of JSON in construction
  for templateNode in metadataTemplate["nodes"]:
    # Split node ID using '#' character
    templateNodeSplitted = templateNode["id"].split('#')
    # Test if split is ok
    try:
      templateNodeSplitted[1]
    except:
      # IF ID cannot be split, current node is a template node. If he is similar to splitted constructed ID, return template node containning all informations for this condition
      if templateNode["id"] == nodeSplitted[1]:
        returnedNode = templateNode
        returnedNode["iteration"] = nodeSplitted[0]
        return returnedNode
    else:
      # Current node is from a particular iteration and not a template node, so mapped DATA is not empty. Still other informations are ok for both nodes. So it can be possible to extract needed informations from this node
      if templateNodeSplitted[1] == nodeSplitted[1]:
        templateNode = {
        "id": templateNodeSplitted[1],
        "cond": templateNode["cond"],
        "mappedData": [],
        "class": templateNode["class"],
        "lbl": templateNode["lbl"],
        "iteration": nodeSplitted[0]
        }
        return templateNode


def calculateNodesValues(jsonFile, sizeOfIterations):
  """Allow to calculate percentage of representation of each experimentation term. To do it, it calculate percentage of genes mapped on current node in relation to the total number of genes

  Parameters
  ----------
  jsonFile : array of dictionnaries
        Array gathering all nodes and links of graph.
  sizeOfIterations : Dictionnary
      Dictionnary with as key iteration number and as value number of experimentations involved in iteration

  Returns
  -------
  jsonFile : array of dictionnaries
        Array gathering all nodes and links of graph with relative value.

  """
  for node in jsonFile["nodes"]:
    # Try to split node ID, if it's not possible because this ID is from metadata template, function will this node
    nodeSplitted = splitNodesId(node)
    if not nodeSplitted:
      continue
    try:
      node["cond"]
    except:
      continue
    else:
      # Access to size of current iteration by reconstructing key of this iteration
      sizeOfCurrentIteration = sizeOfIterations["iteration" + "_" + nodeSplitted[0]]
      # Calculate percentage of representation of given node
      # Save it in node information, rounded at 3 decimals
      node["relativeValue"] = round((len(node["mappedData"]) / sizeOfCurrentIteration) * 100,3)
  return jsonFile


def addExperiments(catmaMetadataJson, metadataTemplate, idOfExperrimentation, constructedId):
  """Allow to add experimentation informations in mappedData array of a given node

  Parameters
  ----------
  constructedId : string
      A string composed by two part: first a number corresponding on iteration where node appear and in second part ID of condition represented by node. Parts are separated using '#' character
  metadataTemplate : Json Object
      A JSON object gathering all possible nodes. Based on Biological insight tree
  catmaMetadataJson : Json Object
      JSON gathering all informations of each experimentations. As key, ID of experimentation, as value an object of metadata
  idOfExperrimentation: string
      A unique ID for experimentation informations. Used as key in catmaMetadataJson
  """
  # Iterate through nodes of JSON in construction
  for templateObject in metadataTemplate["nodes"]:
    # If right experimentation has been found
    if templateObject["id"] == constructedId:
      # Append it in mappedData array of right node
      templateObject["mappedData"].append(
          catmaMetadataJson[idOfExperrimentation])

def getSizeOfCategoryPart(jsonFile,sizeOfCategoryPart):
  """ This function allow to count how many occurences exist in each category for each iterations
  Parameters
  ----------
  corgiExperiments : Dictionnary
      Json with as keys iterations name and in value an array of all experimentation ID involved in iteration
  catmaMetadataJson : Json Object
      JSON gathering all informations of each experimentations. As key, ID of experimentation, as value an object of metadata
  sizeOfCategoryPart : Dictionnary
      A Dictionnary gathering size of each conditions for each iterations. Here is an example of an output
      "sizeOfCategoryPart": {
        "cond3": {
          "iteration_0": 1039,
          "iteration_1": 35,
          "iteration_3": 10,
          "iteration_2": 19
          },
        "cond4": {
          "iteration_0": 1040,
          "iteration_1": 35,
          "iteration_3": 10,
          "iteration_2": 19
          },
          "cond1": {},
          "cond2": {
            "iteration_0": 1042,
            "iteration_1": 35,
            "iteration_3": 10,
            "iteration_2": 19
          }
        }
  """
  for node in jsonFile["nodes"]:
    try:
      sizeOfCategoryPart[node["cond"]]["iteration" + "_" +
                         node["iteration"]]
    except:
      sizeOfCategoryPart[node["cond"]]["iteration" + "_" + node["iteration"]] = 0
      sizeOfCategoryPart[node["cond"]]["iteration" + "_" +node["iteration"]] =sizeOfCategoryPart[node["cond"]]["iteration" + "_" +node["iteration"]]+ len(node["mappedData"])
    else:
      sizeOfCategoryPart[node["cond"]]["iteration" + "_" + node["iteration"]] =sizeOfCategoryPart[node["cond"]]["iteration" + "_" +node["iteration"]]+ len(node["mappedData"])

def getAllNodesFromInput(jsonFile, inputStats):
  """
  """
  for node in jsonFile["nodes"]:
    if node["iteration"] == "0":
      inputStats[node["cond"]][node["lbl"]]=len(node["mappedData"])
      inputStats["total"] +=len(node["mappedData"])
