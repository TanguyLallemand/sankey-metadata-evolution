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
import os
import re


def openJsonFile(filename):
  """Allow to open a Json file and return it loaded in an object.

  Parameters
  ----------
  filename : string
      Path to a Json file.

  Returns
  -------
  Json object
      Return a Json object containning loaded local data

  """
  with open(filename, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
  return(json_data)


def saveJsonFile(filename, jsonObject):
  """Allow to open a Json file and return it loaded in an object.

  Parameters
  ----------
  filename : string
      Path to a Json file.

  Returns
  -------
  Json object
      Return a Json object containning loaded local data

  """
  #
  with open(filename, mode='w+', encoding='utf-8') as outputJson:
    # Dump Json object in a file, add  indent=2, to not minify json
    json.dump(jsonObject, outputJson, separators=(',', ': '))


def parseCorgiOutput(path):
  """Allow to parse CoRGI output file and return parsed information of genes and metadata of experimentations throught all iterations of CoRGI experimentations

  Parameters
  ----------
  path : string
      Path of CoRGI output file

  Returns
  -------
  [experiments, genes] : array
      Return an array containning in first cell a dictionnary of parsed experimentations with iteration number as key and as value an array of parsed metadata of experimentations. Second cell contain gene AT ID in same format as experimentations
  """
  experiments = {"iteration_0": []}
  genes = {"iteration_0": []}
  iteration = "iteration_0"
  i = 0
  with open(path, mode='r') as algorithmOutput:
    for line in algorithmOutput:
      for lineSplitted in line.split():
        if lineSplitted == "Itération":
          i = line.split()[1]
          # iteration = lineSplitted.split('_')[0] + "_" + line.split()[1]
          iteration = "iteration_" + line.split()[1]
          # Initialize a new array of object in both array, to store future IDs of experiments or genes
          experiments[iteration] = []
          genes[iteration] = []
        # If current line is a ID of experiment
        if re.match("^X", lineSplitted):
          # Delete X char, and replace '.' by a '#' to fit with orignals IDs
          lineSplitted = lineSplitted[1:].replace('.', '#')
          # if i != 0:
          experiments[iteration].append(lineSplitted)
        # If current line is a ID of gene
        if re.match("^AT", lineSplitted):
          # if i != 0:
          genes[iteration].append(lineSplitted)
  # Return results in an array of array, allowing a more compact return, easy to parse
  return [experiments, genes]

def constructTAIRDatabaseJson(tsvContent):
  """Allow to construct a Json object from a TSV file from TAIR database and return it loaded in an Json object.

  Parameters
  ----------
  tsvContent : array
      Array containning all data from a CSV

  Returns
  -------
  dictionnary
      Return a Json object gathering all informations for each Gene ID from TAIR database
  """
  # Header of TSV file
  # Locus	Gene Model(s)	GO term (GO ID)	cat	code	GO Slim	Reference	Made by: date last modified
  # One exemple
  # AT5G15930	2146117	AT5G15930	Rab GTPase binding	GO:0017137	8668	func	protein binding	IBA	Communication:501741973		08/03/2018 00:00:00
  # Accesion by index
  #
  # 1. locus name: standard AGI convention name
  # 2. TAIR accession:the unique identifier for an object in the TAIR database-
  # the object type is the prefix, followed by a unique accession number(e.g. gene:12345).
  # 3. object name : the name of the object (gene, protein, locus) being annotated.
  # 4. relationship type: the relationship between the annotated object and the GO term
  # 5. GO term: the actual string of letters corresponding to the GO ID
  # 6. GO ID: the unique identifier for a GO term.
  # 7. TAIR Keyword ID: the unique identifier for a keyword in the TAIR database.
  # 8.  Aspect: F=molecular function, C=cellular component, P=biological 13process.
  # 9. GOslim term: high level GO term helps in functional categorization.
  # 10. Evidence code: three letter code for evidence types (see: http://www.geneontology.org/GO.evidence.html).
  # 11. Evidence description: the analysis that was done to support the annotation
  # 12. Evidence with: supporting evidence for IGI, IPI, IC, IEA and ISS annotations
  # 13. Reference: Either a TAIR accession for a reference (reference table: reference_id) or reference from PubMed (e.g. PMID:1234).
  # 14. Annotator: TAIR, TIGR, GOC (GO Consortium), UniProt, IntAct or a TAIR community member
  # 15. Date annotated: date the annotation was made.
  # Initialize an object to store json in construction
  jsonObject = {}
  # Read TSV content
  for tsvLine in tsvContent:
    tempObject = {}
    if tsvLine[0] not in jsonObject:
      jsonObject[tsvLine[0]] = []
    # If TAIR found a result for this line save it in a dictionnary, with gene ID as key and different informations as value
    # All informations and index to access it are in comments. For this script only usefull informations are saved in order to save more memory
    if len(tsvLine) == 15:
      tempObject["Locus_name"] = tsvLine[0]
      # tempObject["TAIR_accession"] = tsvLine[1]
      # tempObject["Object_name"] = tsvLine[2]
      # tempObject["Relationship_type"] = tsvLine[3]
      tempObject["GO_Term"] = tsvLine[4]
      tempObject["GO_ID"] = tsvLine[5]
      # tempObject["TAIR_Keyword_ID"] = tsvLine[6]
      # tempObject["Aspect"] = tsvLine[7]
      tempObject["GOslim_reference"] = tsvLine[8]
      tempObject["Evidence_code"] = tsvLine[9]
      # tempObject["Evidence_description"] = tsvLine[10]
      # tempObject["Evidence_with"] = tsvLine[11]
      # tempObject["Reference"] = tsvLine[12]
      # tempObject["Annotator"] = tsvLine[13]
      # tempObject["Date_annotated"] = tsvLine[14]
    else:
      tempObject = {"Not Found": "Null"}
    jsonObject[tsvLine[0]].append(tempObject)
  return(jsonObject)
