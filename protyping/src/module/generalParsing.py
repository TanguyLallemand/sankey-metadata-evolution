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
import os
import re


def addEdges(jsonFile):
  """Add edges between nodes if necessary. This means if:
    - Iteration of source node is lower than target node
    - If source and target ndoes have mappedDatas
    - If names are the same

  Parameters
  ----------
  jsonFile : array of dictionnaries
      Array gathering all nodes of graph

  Returns
  -------
  array of dictionnary
      array gathering all links objects
  """
  # Iterate through nodes of JSON in construction
  for node in jsonFile["nodes"]:
    # Try to split node ID
    nodeSplitted = splitNodesId(node)
    # If node ID cannot be splitted go to next one
    if not nodeSplitted:
      continue
    # Get a second node
    for secondNode in jsonFile["nodes"]:
      # Try to split node ID
      secondNodeSplitted = splitNodesId(secondNode)
      # If node ID cannot be splitted go to next one
      if not secondNodeSplitted:
        continue
      # Add edges between nodes if necessary. This means if:
      # - Iteration of source node is lower than target node
      # - If source and target ndoes have mappedDatas
      # - If names are the same
      if nodeSplitted[0] < secondNodeSplitted[0] and len(node["mappedData"]) > 0 and len(secondNode["mappedData"]) > 0 and nodeSplitted[1] == secondNodeSplitted[1]:
        # Construct link
        edge = {"source": nodeSplitted[1], "target": secondNodeSplitted[1],
                "pred": "to_change", "value": 1, "iteration": int(nodeSplitted[0])}
        # If this link does not exist yet, add it in final JSON
        if edge not in jsonFile["links"]:
          jsonFile["links"].append(edge)
  # Add a value too each links
  jsonFile = addEdgeValue(jsonFile)
  return jsonFile


def addEdgeValue(jsonFile):
  """Because Sankey d3.js is based on value of edge instead on source and target node's values, add source relativeValue as value of a link is needed

  Parameters
  ----------
  jsonFile : array
      An array containning in first cell a dictionnary of parsed experimentations with iteration number as key and as value an array of parsed metadata of experimentations. Second cell contain gene AT ID in same format as experimentations

  Returns
  -------
  jsonFile : array
      An array containning in first cell a dictionnary of parsed experimentations with iteration number as key and as value an array of parsed metadata of experimentations. Second cell contain gene AT ID in same format as experimentations
  """
  # Iterate through edges
  for edge in jsonFile["links"]:
    # Iterate through nodes
    for node in jsonFile["nodes"]:
      # If right node is found
      if str(edge["iteration"]) + "#" + edge["source"] == node["id"]:
        # Save value of source node as value of link
        edge["value"] = node["relativeValue"]
  return jsonFile


def splitNodesId(node):
  """Allow to try to split ID of a node decomposing ID and involved iteration based on sperator character ('#'). This function is equipped wit a try block avoiding to crash if script try to split ID of templateNodes that does not have a '#'. In fact, if it possible to access to a second cell, ID is well splitted and fucntion return array of splitted string. Otherwise, node was part of node template and return a false to give to information to script that this ID cannot be splitted

  Parameters
  ----------
  node : dictionnary
      Dictionnary gathering all informations of a node. Here is an example of a node content:
      {"id":"3.3.6", "cond":"cond3", "mappedData":[],"class":"stress", "lbl":"Light (UV...)", "relativeValue":41},

  Returns
  -------
  nodeSplitted : array
      array of strings containning splited ID
  """
  # Split ID using '#' as separator
  nodeSplitted = node["id"].split('#')
  # If it possible to access to a second cell, ID is well splitted and fucntion return array of splitted string. Otherwise, node was part of node template and return a false to give to information to script that this ID cannot be splitted
  try:
    nodeSplitted[1]
  except:
    return False
  else:
    return nodeSplitted


def getSizeOfIterations(iterations):
  """Allow to get size of each iterations of CoRGI algorithm

  Parameters
  ----------
  iterations : dictionnary
      dictionnary gathering all experiments ID for each iterations

  Returns
  -------
  sizeOfIterations : Dictionnary
      Dictionnary with as key iteration number and as value number of experimentations involved in iteration
  """
  sizeOfIterations = {}
  # Iterate through experimentations data
  for experimentsIterator in iterations:
    # Get size of each iterations and strore it in an array
    sizeOfIterations[experimentsIterator] = len(
        iterations[experimentsIterator])
  return sizeOfIterations
