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

import copy
import json

from module.generalParsing import *


def createGeneNodes(geneTemplate, iteration):
  """This function allow to create node with unique IDs for every iteration made by CoRGI and return it in three dictionnaries in node-link format. Every possible nodes are created, useless ones will be deleted by parser in a second time

  Parameters
  ----------
  geneTemplate : dictionnary
      Gathering all informations for nodes of last level of GOSlim
  iteration : dictionnary
      A dictionnary with iterations names as keys and number of genes in each iterations. Here is an example of dictionnary:
      {'iteration_1': 264,
      'iteration_0': 434,
      'iteration_2': 96,
      'iteration_3': 37}

  Returns
  -------
  dictionnary
    A nested dictionnary with a root level the three part of GO as keys and arrays (in node-link format) as values
    {"cellular_component": [
      "nodes": [], "links": []
      ],
      "molecular_function": [
        "nodes": [], "links": []
      ],
      "biological_process": [
        "nodes": [], "links": []
      ]}
  """
  # Initialize an empty node-link dictionnary
  geneDictionnary = {"nodes": [], "links": []}
  # Iterate through iteration dictionnary
  for iterator in iteration:
    # Get current iteration number by splitting dictionnary key
    currentIterationNumber = iterator.split("_")[1]
    # Iterate through nodes template
    for node in geneTemplate:
      # Deep copy node
      newNode = copy.deepcopy(node)
      # Generate a correct ID making an iD like next example:
      # currentIterationNumber#GOid
      newNode["id"] = currentIterationNumber + "#" + node["id"]
      # Add iteration
      newNode["iteration"] = currentIterationNumber
      # Append it in dictionnary
      geneDictionnary["nodes"].append(newNode)
  return geneDictionnary


def mapOnGeneNodes(corgiGenes, geneInformations, sizeOfIterations, genesJson):
  """Map nodes constructed using GOSlim informations and genes coming from each iterations of CoRGI. Those genes are enrichied using informations coming from TAIR database.

  Parameters
  ----------
  corgiGenes : dictionnary
      A dictionnary with iteration number as key and array of gene as value.
      {'iteration_1': [
        'ATG....',
      ],
      'iteration_0': [
      'ATG....'
      ],
      'iteration_2':
      ['ATG....',
      ],
      'iteration_3': [
      'ATG....'
      ]}
  geneInformationsJson : dictionnary
      Dictionnary gathering all informations of every nodes of GOSlim.
  sizeOfIterations : dictionnary
      A dictionnary with iterations names as keys and number of genes in each iterations. Here is an example of dictionnary:
      {'iteration_1': 264,
      'iteration_0': 434,
      'iteration_2': 96,
      'iteration_3': 37}
  genesJson : array of dictionnaries
      Array gathering all nodes and links of graph

  Returns
  -------
  geneInformationsJson : dictionnary
      Dictionnary gathering all informations of every nodes of GOSlim.
  """
  # Iterating tought experiments
  for geneIterator in corgiGenes:
    # Split iteration key to get iteration number
    currentIterationNumber = geneIterator.split("_")[1]
    # Iterating throught all ID of expermimentation for current iteration of CoRGI
    for geneID in corgiGenes[geneIterator]:
      if geneID in geneInformations:
        for geneInformation in geneInformations[geneID]:
          # Try to split GOslim_reference following '|'. In fact, if multiple GOslim_reference exist, they are separated by '|'
          try:
            splitedGeneInformation = geneInformation['GOslim_reference'].split(
                '|')
            splitedGeneInformation[1]
          # If there is no multiple GOslim_reference search for right label and save this gene in mappedData
          except:
            for node in genesJson["nodes"]:
              if splitedGeneInformation[0] == node['lbl'] and node['iteration'] == currentIterationNumber:
                # Append gene information in mappedData array of current node
                appendUniqMappedData(node, geneInformation)
          # If there is multiple GOslim_reference
          else:
            # Loop on every GOslim_reference, search for right GO slim node and save in it gene Informations
            for splittedGeneLbl in splitedGeneInformation:
              for node in genesJson["nodes"]:
                if splittedGeneLbl == node['lbl'] and node['iteration'] == currentIterationNumber:
                  # Append gene information in mappedData array of current node
                  appendUniqMappedData(node, geneInformation)
  # If node does not have any gene mapped in it, delete it
  genesJson = purgeEmptyNodes(genesJson)
  return genesJson

def mapOnGeneNodesCompleteGO(corgiGenes, geneInformations, genesJson):
  """Map nodes constructed using GOSlim informations and genes coming from each iterations of CoRGI. Those genes are enrichied using informations coming from TAIR database.

  Parameters
  ----------
  corgiGenes : dictionnary
      A dictionnary with iteration number as key and array of gene as value.
      {'iteration_1': [
        'ATG....',
      ],
      'iteration_0': [
      'ATG....'
      ],
      'iteration_2':
      ['ATG....',
      ],
      'iteration_3': [
      'ATG....'
      ]}
  geneInformationsJson : dictionnary
      Dictionnary gathering all informations of every nodes of GOSlim.
  genesJson : array of dictionnaries
      Array gathering all nodes and links of graph

  Returns
  -------
  geneInformationsJson : dictionnary
      Dictionnary gathering all informations of every nodes of GOSlim.
  """

  # Iterating throught all ID of expermimentation for current iteration of CoRGI
  for node in genesJson["nodes"]:
    if "mappedData"not in node:
      node["mappedData"]=[]
    for geneID in corgiGenes:
      if geneID in geneInformations:
        for geneInformation in geneInformations[geneID]:
            if geneInformation["GO_ID"] == node['id']:
              # Append gene information in mappedData array of current node
              appendUniqMappedData(node, geneInformation)
              # node["mappedData"].append(geneInformation)
  return genesJson

def purgeEmptyNodes(genesJson):
  """Delete nodes not represented in CoRGI iterations (he does not gather informations in mappedData)

  Parameters
  ----------
  genesJson : array of dictionnaries
      Array gathering all nodes and links of graph

  Returns
  -------
  array of dictionnaries
      Array gathering all nodes and links of graph

  """
  # Iterate through all nodes
  for node in genesJson["nodes"]:
    # If there is not mapped genes
    if len(node["mappedData"]) == 0:
      # Remove node
      genesJson["nodes"].remove(node)
  return genesJson


def appendUniqMappedData(node, geneInformation):
  seen = set()
  for dic in node["mappedData"]:
    key = (dic['Locus_name'], dic['GO_ID'])
    seen.add(key)

  geneInformationKey = (geneInformation["Locus_name"],geneInformation["GO_ID"])
  if geneInformationKey not in seen:
    print("Added: "+ geneInformation["GO_ID"] + " in " + node["lbl"] )
    node["mappedData"].append(geneInformation)



def prepareGeneTemplate(geneInformationsJson):
  """Construct a nested dictionnary gathering templates of all nodes of last level of GOSlim and put it in right dictionnary following his category in Gene Ontology (cellular_component, molecular_function or biological_process)

  Parameters
  ----------
  geneInformationsJson : dictionnary
      Dictionnary gathering all informations of every nodes of GOSlim

  Returns
  -------
  dictionnary
      A nested dictionnary with a root level the three part of GO as keys and arrays (in node-link format) as values
      {"cellular_component": [
        "nodes": [], "links": []
        ],
        "molecular_function": [
          "nodes": [], "links": []
        ],
        "biological_process": [
          "nodes": [], "links": []
        ]}

  """
  # Initialize a dictionnary of array
  constructedGenesTemplate = {"cellular_component": [],
                              "molecular_function": [],
                              "biological_process": []}
  # Iterate through all genes
  for geneInformations in geneInformationsJson["nodes"]:
   # If there is more than this infos in basicPropertyValues loop on it until find to which GO part this node belongs
    for i in range(0, len(geneInformations["meta"]["basicPropertyValues"])):
      # If part of GO implicated is stored in meta dictionnary of node
      if geneInformations["meta"]["basicPropertyValues"][i]["pred"] == 'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace':
        geneInformations["GOPart"]=geneInformations["meta"]["basicPropertyValues"][i]["val"]
        # Put gene in right array using meta information
        constructedGenesTemplate[geneInformations["meta"]
                                 ["basicPropertyValues"][i]["val"]].append(geneInformations)
  return constructedGenesTemplate


def getSizeOfGOParts(sizeOfGOPart, jsonFile):
  """For each part of GO calculate how many genes are mapped on each GOSlim term at each iterations.

  Parameters
  ----------
  sizeOfGOPart : type
      Description of parameter `sizeOfGOPart`.
  jsonFile : array of dictionnaries
        Array gathering all nodes and links of graph
  """
  for node in jsonFile["nodes"]:
    try:
      sizeOfGOPart[node["GOPart"]]["iteration" + "_" +
                         node["iteration"]]
    except:
      sizeOfGOPart[node["GOPart"]]["iteration" + "_" + node["iteration"]] = 0
      sizeOfGOPart[node["GOPart"]]["iteration" + "_" +node["iteration"]] =sizeOfGOPart[node["GOPart"]]["iteration" + "_" +node["iteration"]]+ len(node["mappedData"])
    else:
      sizeOfGOPart[node["GOPart"]]["iteration" + "_" + node["iteration"]] =sizeOfGOPart[node["GOPart"]]["iteration" + "_" +node["iteration"]]+ len(node["mappedData"])


def addRelativeValueForGOParts(sizeOfGOPart, jsonFile, name):
  """ Calculate for each part of GO percentage of representation of each GO term. To do it, it calculate percentage of genes mapped on current GO term in relation to the total number of genes

  Parameters
  ----------
  sizeOfGOPart : dictionnary
      Describe How many genes are mapped on each GO part for each iteration
        {
        'biological_process': {
          'iteration_1': 35,
          'iteration_2': 11,
          'iteration_3': 1,
          'iteration_0': 69},
        'cellular_component': {
          'iteration_1': 620,
          'iteration_2': 294,
          'iteration_3': 128,
          'iteration_0': 901},
        'molecular_function': {
          'iteration_1': 46,
          'iteration_2': 20,
          'iteration_3': 2,
          'iteration_0': 80}
        }
  jsonFile : array of dictionnaries
        Array gathering all nodes and links of graph
  name : string
      Indicates in which part of GO nodes belongs

  Returns
  -------
  jsonFile : array of dictionnaries
        Array gathering all weighted nodes and links of graph
  """
  for node in jsonFile["nodes"]:
    # Calculate percentage of representation of given node.
    # Save it in node information, rounded at 3 decimals
    try:
      node["relativeValue"] = round(
          (len(node["mappedData"]) / sizeOfGOPart[name]["iteration" + "_" + node["iteration"]]) * 100, 3)
    except:
      node["relativeValue"]=0
  return jsonFile


def getAllNodesFromInput(jsonFile, inputStats):
  """
  """
  for node in jsonFile["nodes"]:
    if node["iteration"] == "0":
      inputStats[node["GOPart"]][node["lbl"]]=len(node["mappedData"])
      inputStats["total"] +=len(node["mappedData"])
