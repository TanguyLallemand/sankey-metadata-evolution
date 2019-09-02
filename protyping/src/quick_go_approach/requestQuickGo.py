# -*- coding: utf-8 -*-
# Author: Tanguy Lallemand
import requests

def requestGeneProduct(query):
  """Allow to request QuickGo API for searching the gene product data-set for a specified value .

    Parameters
    ----------
    query : string
        The query used to filter the gene products.

    Returns
    -------
    Json-like object
        An object containning response body from QuickGO's server.

  """
  # Construct query string by binding URL with query string
  requestURL = "https://www.ebi.ac.uk/QuickGO/services/geneproduct/search?query=" + query
  # Send request, asking for a result in Json format
  r = requests.get(requestURL, headers={"Accept": "application/json"})
  # Handle with errors
  if not r.ok:
    r.raise_for_status()
    sys.exit()
  # Parse response and return it
  responseBody = r.text
  return(responseBody)


def requestAnnotation(query):
  """Allow to request QuickGo API. Annotation result set has been filtered according to the provided attribute values.

    Parameters
    ----------
    query : string
        The id of the gene product annotated with the GO term. Accepts comma separated values.E.g., URS00000064B1_559292.

    Returns
    -------
    Json-like object
        An object containning response body from QuickGO's server.

  """
  # Construct query string by binding URL with query string
  requestURL = "https://www.ebi.ac.uk/QuickGO/services/annotation/search?geneProductId=" + query
  # Send request, asking for a result in Json format
  r = requests.get(requestURL, headers={"Accept": "application/json"})
  # Handle with errors
  if not r.ok:
    r.raise_for_status()
    sys.exit()
  # Parse response and return it
  responseBody = r.text
  return(responseBody)
