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

def deleteUselessInformations(GOJson):
  """Allow to minify more output Json file by deleting useless informations

  Parameters
  ----------
  GOJson : dictionnary
      A dictionnary storing GO in Json format

  Returns
  -------
  GOJson : dictionnary
      Return a modified dictionnary with less useless informations
  """
  for nodes in GOJson["nodes"]:
    if 'meta' in nodes:
      if 'synonyms' in nodes["meta"]:
        del nodes["meta"]["synonyms"]
      if 'xrefs' in nodes["meta"]:
        del nodes["meta"]["xrefs"]
  return GOJson


def mappingGeneOnGO(GOJson, geneInformationsJson, type):
  """Allow to map Genes from TAIR database and their informations in Json of GO

  Parameters
  ----------
  GOJson : dictionnary
      A dictionnary storing GO in Json format
  geneInformationsJson : dictionnary
      A dictionnary storing informations of genes from TAIR database

  Returns
  -------
  GOJson : dictionnary
      Return a modified dictionnary gathering for each node a mappedData array containning all genes mapped on it
  """
  if type ==0:
    ontologyType = 'GOslim_reference'
    accession = "lbl"
  else:
    ontologyType = "GO_ID"
    accession = "id"
  # Loop on nodes of Gene Ontology
  for nodes in GOJson:
    # Initialize an array to store TAIR genes
    mappedData = []
    alreadyMapped=[]
    # Iterate through geneInformationsJson to get keys that are geneID
    for geneID in geneInformationsJson:
      # Iterate through data of each gene
      for GIInformations in geneInformationsJson[geneID]:
        # Try to split GOslim_reference following '|'. In fact, if multiple GOslim_reference exist, they are separated by '|'
        try:
          splitedGIInformations = GIInformations[ontologyType].split(
              '|')
          splitedGIInformations[1]
        # If there is no multiple GOslim_reference search for right label and save this gene in mappedData. This case can also handle when map on complete gene ontology.
        except:
          if 'Not Found' not in GIInformations:
            # Map gene on a node of GOSlim
            if GIInformations[ontologyType] == nodes[accession] and GIInformations["Locus_name"] not in alreadyMapped:
              # Some verbose for user, allowing to follow algorithm work
              print("Mapping following gene: " + GIInformations["Locus_name"])
              # Store gene ID of mapped gene in oreder to avoid multiple similar entries
              alreadyMapped=GIInformations["Locus_name"]
              # Store mapped gene and their informations
              mappedData.append(GIInformations)
        # If there is multiple GOslim_reference
        else:
          # Loop on every GOslim_reference, search for right GO slim node and save in it gene Informations
          for i in range(0, len(splitedGIInformations)):
            if 'Not Found' not in GIInformations:
              # Map gene on a node of GOSlim
              if splitedGIInformations[i] == nodes[accession] and GIInformations["Locus_name"] not in alreadyMapped:
                # Some verbose for user, allowing to follow algorithm work
                print("Mapping following gene: " + GIInformations["Locus_name"])
                # Store gene ID of mapped gene in oreder to avoid multiple similar entries
                alreadyMapped=GIInformations["Locus_name"]
                # Store mapped gene and their informations
                mappedData.append(GIInformations)
    # Add mapped genes to GOJson to construct a global Json, result of mapping
    nodes['mappedData'] = mappedData



def calculateEdgesValues(GOJson):
  """Allow to calculate value of each links by calculating number of mapped genes on source and target, add this result in edges dictionnary

  Parameters
  ----------
  GOJson : dictionnary
      A dictionnary storing GO in Json format

  Returns
  -------
  GOJson : dictionnary
      Return a modified dictionnary gathering for each edges weight of it
  """
  # Loop trought edges of Gene Ontology
  for edges in GOJson['edges']:
    # Initialize needed variables
    numberOfNodesSource = None
    numberOfNodesTarget = None
    diffEdge = None
    # Loop trought nodes of Gene Ontology
    for nodes in GOJson['nodes']:
      # If nodes represented as a edge source is found
      if (nodes["id"] == edges["source"]):
        # Save number of mapped genes on it
        numberOfNodesSource = len(nodes["mappedData"])
      # If nodes represented as a edge source is found
      if (nodes["id"] == edges["target"]):
        # Save number of mapped genes on it
        numberOfNodesTarget = len(nodes["mappedData"])
      # If nodes are not yet found continue to loop
      if numberOfNodesTarget is None or numberOfNodesSource is None:
        continue
      # If diff edge has not been calculated
      elif diffEdge is None:
        diffEdge = numberOfNodesTarget - numberOfNodesSource
        # Save absolute value of difference between number of genes mapped in source and target
        edges["value"] = abs(diffEdge)
    return GOJson
