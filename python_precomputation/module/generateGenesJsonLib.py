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


def constructGenesJson(catmaJsonFile, tairDatabase):
  """Allow to add more informations in catma file using TAIR database annotations.

  Parameters
  ----------
  catmaJsonFile : dictionnary
      dictionnary gathering informations about all genes in CoRGI's matrix. Each gene are like following example:
      "AT1G01010": {
        "probe": "CATMA1A00010"
      }

  tairDatabase : array
      Array containning all data from a CSV

  Returns
  -------
  dictionnary
      Return a Json object gathering all informations for each Gene ID from TAIR database

        "AT1G15630": {
          "GOslim_reference": "unknown molecular functions",
          "GO_ID": "GO:0003674",
          "Evidence_code": "ND",
          "probe": "CATMA1D02515"
        },
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
  # Read TSV content
  for tsvLine in tairDatabase:
    # If TAIR found a result for this line save it in a dictionnary, with gene ID as key and different informations as value
    # All informations and index to access it are in comments. For this script only usefull informations are saved in order to save more memory
    if len(tsvLine) == 15:
      if tsvLine[0] in catmaJsonFile:
        if "GO_ID" not in catmaJsonFile[tsvLine[0]]:
          catmaJsonFile[tsvLine[0]]["GO_ID"] = []
          catmaJsonFile[tsvLine[0]]["GOslim_reference"] = []
          catmaJsonFile[tsvLine[0]]["Evidence_code"] = []
        if tsvLine[5] not in catmaJsonFile[tsvLine[0]]["GO_ID"]:
          # catmaJsonFile[tsvLine[0]]["Locus_name"] = tsvLine[0]
          # catmaJsonFile[tsvLine[0]]["TAIR_accession"] = tsvLine[1]
          # catmaJsonFile[tsvLine[0]]["Object_name"] = tsvLine[2]
          # catmaJsonFile[tsvLine[0]]["Relationship_type"] = tsvLine[3]
          # catmaJsonFile[tsvLine[0]]["GO_Term"] = tsvLine[4]
          catmaJsonFile[tsvLine[0]]["GO_ID"].append(tsvLine[5])
          # catmaJsonFile[tsvLine[0]]["TAIR_Keyword_ID"] = tsvLine[6]
          # catmaJsonFile[tsvLine[0]]["Aspect"] = tsvLine[7]
          catmaJsonFile[tsvLine[0]]["GOslim_reference"].append(tsvLine[8])
          catmaJsonFile[tsvLine[0]]["Evidence_code"].append(tsvLine[9])
          # catmaJsonFile[tsvLine[0]]["Evidence_description"] = tsvLine[10]
          # catmaJsonFile[tsvLine[0]]["Evidence_with"] = tsvLine[11]
          # catmaJsonFile[tsvLine[0]]["Reference"] = tsvLine[12]
          # catmaJsonFile[tsvLine[0]]["Annotator"] = tsvLine[13]
          # catmaJsonFile[tsvLine[0]]["Date_annotated"] = tsvLine[14]
  return(catmaJsonFile)
