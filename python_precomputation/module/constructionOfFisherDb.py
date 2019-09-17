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


def parseTAIRDatabase(TAIRJson, TAIRDatabase):
  """
  Count every occurence of every GO slim term in TAIR database
  Parameters
  ----------
  TAIRJson : dicctionnary of arrays
      A dictionnary storing all TAIR annotations
  TAIRDatabase: dictionnary
      Empty dictionnary created to store output json object
  Returns
  -------
  dictionnary
      Return a Json object gathering count of all GO Slim terms found in TAIR database
  """
  # Iteration throught TAIR database object
  for geneID in TAIRJson:
    for GOentry in TAIRJson[geneID]:
      # Try to get a GOslim_reference
      try:
        GOentry["GOslim_reference"]
      except:
        continue
      # If this Go SLim term does not exist yet in output dictionnary, create it
      if GOentry["GOslim_reference"] not in TAIRDatabase:
        TAIRDatabase[GOentry["GOslim_reference"]] = 1
      # If this Go SLim term already exist just count it
      else:
        TAIRDatabase[GOentry["GOslim_reference"]
                     ] = TAIRDatabase[GOentry["GOslim_reference"]] + 1
      TAIRDatabase["total"] = TAIRDatabase["total"] + 1


def parseCoRGIExperiments(catmaMetadataJson, corgiExperiments, TAIRDatabase, metadataTemplate):
  """Allow to create all nodes to visualize evolution of metadata conditions. This algorithm keeps in mind the fact that data are sequential and create nodes for each iterations

  Parameters
  ----------
  corgiExperiments : Dictionnary
      Json with as keys iterations name and in value an array of all experimentation ID involved in iteration
  catmaMetadataJson : Dictionnary
      JSON gathering all informations of each experimentations. As key, ID of experimentation, as value an object of metadata
  metadataTemplate : Dictionnary
      A JSON object gathering all possible nodes. Based on Biological insight tree
  TAIRDatabase: dictionnary
      A Dictionnary storing all occurences count for GO Slim terms and experiments category.
  """
  # Iterating through experiments
  for experimentsIterator in corgiExperiments:
    # Split iteration key to get iteration number
    currentIterationNumber = experimentsIterator.split("_")[1]
    # Iterating through all ID of expermimentation for current iteration of CoRGI
    for idOfExperrimentation in corgiExperiments[experimentsIterator]:
      # Iterating through four possible conditions
      for i in range(1, 5):
        # Try to check if current condition exist
        try:
          catmaMetadataJson[idOfExperrimentation]["cond" + str(i)][0]
        # If condition not exist pass to next condition
        except:
          pass
        else:
          # Iterating through nodes of metadata template
          for node in metadataTemplate["nodes"]:
            # If right node template is found
            # node["id"]=2.2.4
            # str(i)=2
            # catmaMetadataJson["1#2#4"]["cond2"]=2.4
            if node["id"] == str(i) + "." + catmaMetadataJson[idOfExperrimentation]["cond" + str(i)][0]:
              category = node["lbl"]
          # If this label does not exist yet in occurence count
          if category not in TAIRDatabase:
            # Initialize it, and add first occurence
            TAIRDatabase[category] = 1
          else:
            # Add one occurence
            TAIRDatabase[category] = TAIRDatabase[category] + 1
      # Count also total of occurences
      TAIRDatabase["total"] = TAIRDatabase["total"] + 1
