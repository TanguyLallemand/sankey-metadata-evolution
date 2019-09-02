# -*- coding: utf-8 -*-
# Author: Tanguy Lallemand
import json


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

def constructionOfJsonObject(jsonAnswer, origin, initalJsonIterator, jsonObject):
  print("Computing: " + initalJsonIterator["atg"])
  if origin == "annotations":
    # Iterate tought annotations results
    for annotationIterator in jsonAnswer['results']:
    # Append in final array in right place
      for i in jsonObject:
        if i["atg"] == initalJsonIterator["atg"]:
          i["annotations"].append(annotationIterator)
    return jsonObject
  elif origin == "gene_product":
    # Initalization of a temporary object to construct output Json
    resultObject = {}
    # Construct object to save using current results but adding also inital datas
    resultObject["gene_product"] = jsonAnswer
    resultObject["probe"]=initalJsonIterator["probe"]
    resultObject["atg"]=initalJsonIterator["atg"]
    resultObject["annotations"]=[]
    # Add temporary object in output array
    jsonObject.append(resultObject)
    return jsonObject
