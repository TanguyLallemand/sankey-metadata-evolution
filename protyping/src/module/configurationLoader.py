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

import argparse
import configparser


def getCompleteGOThroughTimeArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  # Store a path to store downloaded file
  parser.add_argument(
      "-p", "--GOpath", help="Give a path to store downloaded Json from Gene Ontology", type=str, action='store', nargs='?', default=config["default_settings"]["GOpath"])
  # Store an url in order to download an ontology in Json format
  parser.add_argument(
      "-u", "--url", help="Give an url in order to download an ontology in Json format", type=str, action='store', nargs='?', default=config["default_settings"]["GOurl"])
  parser.add_argument(
      "-d", "--database", help="Give a path to TAIR database file, stored in TSV format", type=str, action='store', nargs='?', default=config["default_settings"]["TAIRDatabase"])
  parser.add_argument(
      "-c", "--corgiPath", help="Give a path to access to CoRGI output file", type=str, action='store', nargs='?', default=config["default_settings"]["corgiOutput"])
  args = parser.parse_args()
  return args

def getTAIRArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  # Store a path to store downloaded file
  parser.add_argument(
      "-p", "--GOpath", help="Give a path to store downloaded Json from Gene Ontology", type=str, action='store', nargs='?', default=config["default_settings"]["GOpath"])
  # Store an url in order to download an ontology in Json format
  parser.add_argument(
      "-u", "--url", help="Give an url in order to download an ontology in Json format", type=str, action='store', nargs='?', default=config["default_settings"]["GOurl"])
  parser.add_argument(
       "-t", "--type", help="Give 0 if computing a Go Slim and 1 if it is a complete ontology", type=int, action='store', nargs='?', default=0)
  parser.add_argument(
      "-d", "--database", help="Give a path to TAIR database file, stored in TSV format", type=str, action='store', nargs='?', default=config["default_settings"]["TAIRDatabase"])

  args = parser.parse_args()
  return args

def getMetadataArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "-p", "--metadataPath", help="Give a path to access to metadata file", type=str, action='store', nargs='?', default=config["default_settings"]["metadataPath"])
  parser.add_argument(
      "-t", "--metadataTemplate", help="Give a path to access to a template of metadata file needed by d3.js", type=str, action='store', nargs='?', default=config["default_settings"]["metadataTemplate"])
  parser.add_argument(
      "-c", "--corgiPath", help="Give a path to access to CoRGI output file", type=str, action='store', nargs='?', default=config["default_settings"]["corgiOutput"])
  parser.add_argument(
      "-o", "--outputPath", help="Give a path to output JSON file", type=str, action='store', nargs='?', default=config["default_settings"]["metadataJsonOutputPath"])
  args = parser.parse_args()
  return args

def getGenesArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "-c", "--corgiPath", help="Give a path to access to CoRGI output file", type=str, action='store', nargs='?', default=config["default_settings"]["corgiOutput"])
  parser.add_argument(
      "-o", "--outputPath", help="Give a path to output JSON file", type=str, action='store', nargs='?', default=config["default_settings"]["genesJsonOutputPath"])
  parser.add_argument(
      "-g", "--geneTemplate", help="Give a path to gene template JSON file", type=str, action='store', nargs='?', default=config["default_settings"]["geneTemplate"])
  args = parser.parse_args()
  return args

def getFisherDatasetArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "-d", "--database", help="Give a path to TAIR database file, stored in TSV format", type=str, action='store', nargs='?', default=config["default_settings"]["TAIRDatabase"])
  parser.add_argument(
      "-c", "--corgiPath", help="Give a path to access to CoRGI output file", type=str, action='store', nargs='?', default=config["default_settings"]["corgiOutput"])
  parser.add_argument(
      "-p", "--metadataPath", help="Give a path to access to metadata file", type=str, action='store', nargs='?', default=config["default_settings"]["metadataPath"])
  parser.add_argument(
      "-t", "--metadataTemplate", help="Give a path to access to a template of metadata file ", type=str, action='store', nargs='?', default=config["default_settings"]["metadataTemplate"])
  args = parser.parse_args()
  return args

def getGOSlimRootedArguments(config):
  """Allow to construct a parser of arguments, generate associated help and a default value coming from config file if no arguments are given.

  Parameters
  ----------
  config : object
      Loaded config object

  Returns
  -------
  Argument object
      Return an argument object containning loaded arguments
  """
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "-g", "--GOfile", help="Give a path to GO json file with mapped genes", type=str, action='store', nargs='?', default=config["default_settings"]["GOAndMappedGenesJson"])
  parser.add_argument(
      "-t", "--geneTemplate", help="Give a path to gene template JSON file gathering GO slim terms", type=str, action='store', nargs='?', default=config["default_settings"]["geneTemplate"])
  args = parser.parse_args()
  return args

def loadConfig(configPath):
  """Allow to open a ini file and return it as a loaded dictionnary of configuration.

  Parameters
  ----------
  configPath : string
      Path to config file

  Returns
  -------
  Config object
      Return a Config object containning loaded local config
  """
  config = configparser.ConfigParser()
  config.sections()
  config.read(configPath)
  return(config)
