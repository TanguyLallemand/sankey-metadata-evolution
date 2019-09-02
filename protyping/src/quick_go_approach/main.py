#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Tanguy Lallemand
import json
import sys
from pprint import pprint

from importExportData import *
from requestQuickGo import requestAnnotation, requestGeneProduct

jsonData = []
# Load Json file given in parameter
# jsonFile = openJsonFile('data/initial/catma5_probes.json')
jsonFile = openJsonFile('data/samples/inital_data.json')
with open('./data/output/enrichied_datas.json', mode='w+') as json_result:
  # Iterate tought local Json file, allowing to get gene product ID
  for initalJsonIterator in jsonFile.values():
    # Request for gene product using gene ID from Json file. Get result and transform it in a Json object
    resultRequestGeneProduct = json.loads(
        requestGeneProduct(initalJsonIterator["atg"]))
    # Iterate tought results of gene products informations
    for geneProductIterator in resultRequestGeneProduct['results']:
      jsonData = constructionOfJsonObject(
          geneProductIterator, "gene_product", initalJsonIterator, jsonData)
      # If gene ID fit with uniprot database, try to get annotations
      if geneProductIterator['database'] == "UniProtKB":
        # Request for gene product using gene ID from Json file. Get result and transform it in a Json object
        resultRequestAnnotation = json.loads(
            requestAnnotation(geneProductIterator['id']))
        constructionOfJsonObject(
            resultRequestAnnotation, "annotations", initalJsonIterator, jsonData)
  # Dump whole data in a Json file
  json.dump(jsonData, json_result, indent=2, separators=(',', ': '))
