/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */

//******************************************************************************
// Prepare Data
//******************************************************************************

// Load config file using D3V5 standard based on promise. Note that you don’t need to rethrow the error—the promise will reject automatically, and you can promise.catch if desired.
d3.json("../conf/config_file_sankey.json").then(function(confJson) {
  // Load file used for compute Fisher test
  d3.json(confJson["paths"]["fisherDataset"]).then(function(fisherDataset) {
    // Load CoRGI output file
    d3.json(confJson["paths"]["corgiOutput"]).then(function(corgiOutput) {
      // Load gene nodes template file
      d3.json(confJson["paths"]["geneOntologyTemplate"]).then(function(geneOntologyTemplate) {
        // Load genes and associated annotations
        d3.json(confJson["paths"]["catmaJsonFileGenes"]).then(function(catmaJsonFile) {
          // Parsing step, preparation of object fitting with d3.js sankey requirements
          var genesWholeJson = generateEvolutionJson(geneOntologyTemplate, corgiOutput, catmaJsonFile, "genes");
          // Construct Sankey diagram in SVG
          generateSankeyDiagram(confJson, genesWholeJson, fisherDataset["TAIRDb"], corgiOutput.genes);
          // Debug
          console.log(genesWholeJson);
          console.log(fisherDataset);
        });
      });
      // Load gene nodes template file
      d3.json(confJson["paths"]["metadataTemplate"]).then(function(metadataTemplate) {
        // Load genes and associated annotations
        d3.json(confJson["paths"]["catmaJsonFileExperiments"]).then(function(catmaJsonFile) {
          // Parsing step, prepaation of object fitting with d3.js sankey requirements
          var experimentsWholeJson = generateEvolutionJson(metadataTemplate, corgiOutput, catmaJsonFile, "experimentations");
          // Construct Sankey diagram in SVG
          generateSankeyDiagram(confJson, experimentsWholeJson, fisherDataset["CoRGIExperiments"], corgiOutput.experimentations);
          // Debug
          console.log(experimentsWholeJson);
        });
      });
    });
  });
});