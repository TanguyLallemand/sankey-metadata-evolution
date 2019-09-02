/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */

/**
 * [generateEvolutionJson description]
 * @param  {Object} geneOntologyTemplate [description]
 * @param  {Object} corgiOutput  An object storing for each iterations of CoRGI
 * algorithm output list of genes and experimentations that are kept in matrix.
 * @param  {Object} catmaJsonFile An object storing catma gene file. This
 * object store as key a gene ID and has value different annotations metadata
 * (probe ID, GO ID and associated evidence code and his GOSlim reference)
 * extracted from TAIR database.
 * @param  {string} graphType Can be "experimentations" or "genes", used to
 * indicate to this script which object is constructed
 * @return {Object} Object storing all informations needed to
 * construct a Sankey diagram
 */
function generateEvolutionJson(geneOntologyTemplate, corgiOutput, catmaJsonFile, graphType) {
  //****************************************************************************
  // Storing object generation
  // Generate an object to store all parsed data in a format readable by the
  // remaining part of the algorithm. Generated object depends on graphType
  //****************************************************************************
  if (graphType == 'genes') {
    var metadataWholeJson = goObject();
  } else {
    var metadataWholeJson = experimentsObject();
  };

  // Determine how many iterations CoRGI has done and count number of occurences of experiments/gene for each iterations
  getSizeOfIterations(corgiOutput[graphType], metadataWholeJson["iteration"]);
  // Iterate through each part (conditions: cond1,cond2,cond3,cond4)
  // or GOParts(molecular_function, biological_process, cellular_component)
  for (var part in metadataWholeJson["sizeOfEachPart"]) {
    // Create all nodes with a unique ID in right part. Uniq ID is composed by GO ID or Experimentations ID and an iteration number separated by '#'
    metadataWholeJson["graph"][part] = createNodes(geneOntologyTemplate[part], metadataWholeJson["iteration"]);
    // Add enrichied genes from CoRGI output of each iteration in right GOSlim term
    if (graphType == 'genes') {
      resetIterationsCounts(metadataWholeJson["iteration"]);
      metadataWholeJson["graph"][part] = mapOnGeneNodes(
        corgiOutput[graphType], catmaJsonFile, metadataWholeJson["graph"][part]);
      getSizeOfGenesIterations(metadataWholeJson["graph"][part], metadataWholeJson["iteration"]);
    } else {
      mapOnExperimentationsNodes(
        corgiOutput[graphType], catmaJsonFile, metadataWholeJson["graph"][part], part);

    };
    // If node does not have any gene mapped in it, delete it
    purgeEmptyNodes(metadataWholeJson["graph"][part]);
    // Add edges between nodes if somes conditions are filled
    addEdges(metadataWholeJson["graph"][part]);
    if (graphType == 'genes') {
      // Get all nodes that belongs to iteration_0 (input) and use their label as key and number of occurences mapped on it as value. Tbhis object is used to compute Fisher exact test against input dataset
      getAllNodesFromInput(metadataWholeJson["graph"][part], metadataWholeJson["inputDataset"], "GOPart");
    } else {
      // Get all nodes that belongs to iteration_0 (input) and use their label as key and number of occurences mapped on it as value. Tbhis object is used to compute Fisher exact test against input dataset
      getAllNodesFromInput(metadataWholeJson["graph"][part], metadataWholeJson["inputDataset"], "cond");
    };
  };
  // Get number of occurences (genes or experimentations) mapped on each part
  getSizeOfEachPart(metadataWholeJson);
  // Calculate a relative value for each node. This value will be used to determine node height in sankey diagram. Relative value is calculated following this formula: (number of occurence mapped on a given node * 100 / number of occurences mapped on current iteration)
  addRelativeValueForGOParts(metadataWholeJson);
  return metadataWholeJson;
};


/**
 * mapOnGeneNodes is a function to assign to each node of the last level of the
 * GOSlim plant all the genes that have been annotated with this GOSlim
 * reference term. Annotations comes from TAIR database. All annotated genes
 * and their associated data are stored in an object that will be placed in the
 * mappedData array of the corresponding node.
 *
 *
 * Here is an example of informations stored for each genes in catma file:
 * *Sample*
 * <pre class='json'>
 * "AT1G01010": {
 *  "probe": "CATMA1A00010",
 *  "GO_ID": [
 *    "GO:0006355",
 *    "GO:0016021",
 *    "GO:0005634",
 *    "GO:0003677",
 *    "GO:0003700"
 *  ],
 *  "GOslim_reference": [
 *    "biosynthetic process",
 *    "other membranes",
 *    "nucleus",
 *    "DNA binding",
 *    "DNA-binding transcription factor activity"
 *  ],
 *  "Evidence_code": [
 *    "IEA",
 *    "IEA",
 *    "ISM",
 *    "IEA",
 *    "ISS"
 *  ]
 *},
 * </pre>
 *
 * @param  {Object} corgiOutput  An object storing for each iterations of CoRGI algorithm output list of genes and experimentations that are kept in matrix.
 * @param  {Object} geneInformations An object storing catma gene file. This
 * object store as key a gene ID and as value different annotations metadata
 * (probe ID, GO ID and associated evidence code and his GOSlim reference)
 * extracted from TAIR database.
 * @param  {Object} genesJson An object in nodes-links format (to remember:
 *  {
 *    "nodes": [],
 *    "links": []
 *  })
 * @return {Object} An object in nodes-links format where each nodes of graph contains in an array (mappedData) all annotated genes on it.
 */
function mapOnGeneNodes(corgiOutput, geneInformations, genesJson) {
  for (var iteration in corgiOutput) {
    // Iterating throught all ID of expermimentation for current iteration of CoRGI
    corgiOutput[iteration].forEach(function(geneID) {
      if (geneID in geneInformations && "GOslim_reference" in geneInformations[geneID]) {
        // Allowing to get goslim reference and fit with all cases
        geneInformations[geneID]["GOslim_reference"].forEach(function(GOslim_reference) {
          genesJson["nodes"].forEach(function(node) {
            // Split iteration key to get iteration number
            if (GOslim_reference == node['lbl'] && node['iteration'] == iteration.split("_")[1]) {
              node["mappedData"].push(getGeneInformationObject(geneInformations[geneID], geneID, GOslim_reference));
            };
          });
        });
      };
    });
  };
  return genesJson;
};
/**
 * Construct an object gathering one annotation of current gene using TAIR
 * database's informations
 * @param  {Object} geneInformationsCompleteObject Object storing annotations
 * for current genes from TAIR database.
 * @param  {string} geneID Gene ID of current gene. Looks like following example: AT1G01010.
 * @param  {string} GOslim_reference_lbl Label of GosSlim term used as
 * reference for current node
 * @return {Object} An object gathering one annotation of current gene like following example:
 * [
 *  {
 *    Evidence_code: "IMP",
 *    GO_ID: "GO:0008219"
 *    Gene_ID: "AT1G55490"
 *    probe: "CATMA1B46590"
 *  }
 * ]
 */
function getGeneInformationObject(geneInformationsCompleteObject, geneID, GOslim_reference_lbl) {
  // All annotations are stored in each arrays following same index. In order
  // to get informations of one annotation, need to get index of one of those
  // informations and get all associated data using same index in each arrays
  var indexOfGOSlim = geneInformationsCompleteObject["GOslim_reference"].indexOf(GOslim_reference_lbl);
  return {
    "Evidence_code": geneInformationsCompleteObject["Evidence_code"][indexOfGOSlim],
    "Gene_ID": geneID,
    "GO_ID": geneInformationsCompleteObject["GO_ID"][indexOfGOSlim],
    "probe": geneInformationsCompleteObject["probe"]
    // "GOslim_reference": geneInformationsCompleteObject["GOslim_reference"][indexOfGOSlim]
  };
};
/**
 * mapOnExperimentationsNodes is a function to assign to each node of the
 * metadata tree all experimentations that have been annotated with this
 * condition. Annotations comes catma experimentations files. All those
 * metadatas are stored in objects like following one:
 *
 * Here is an example of informations stored for each experimentations in catma
 * file:
 * *Sample*
 * <pre class='json'>
 * "0#0#1338": {
 *   "cond1": "",
 *   "cond2": [
 *   "2.2",
 *   ""
 *   ],
 *   "cond3": [
 *   "1",
 *   ""
 *   ],
 * "cond4": "0",
 * "control": "stem_2",
 * "experiment": "stem developement",
 * "keywords": "10cm/2cm",
 * "link": "http://tools.ips2.u-psud.fr/cgi-bin/projects/CATdb/consult_expce.pl?experiment_id=0#1338",
 * "projet": "AF09_lignin",
 * "swap": "stem_10 / stem_2",
 * "treatment": "stem_10",
 * "type": "microarray",
 * "warning": ""
 * },
 * </pre>
 * @param  {Object} corgiOutput  An object storing for each iterations of CoRGI
 * algorithm output list of genes and experimentations that are kept in matrix.
 * @param  {Object} experimentationsInformations An object storing catma
 * experimentations file. This object store as key an experimentations ID and
 * as value different annotations metadata.
 * @param  {Object} experimentationsJson         [description]
 * @param  {String} condition condition string like cond1. Used to split on 'd'
 * char and get current condition number.
 * @return {Object} An object in nodes-links format where each nodes of graph contains in an array (mappedData) all annotated experimentations on it.
 */
function mapOnExperimentationsNodes(corgiOutput, experimentationsInformations, experimentationsJson, condition) {
  // Split condition code using 'd' char allowing to get condition number of current nodes
  var conditionNumber = condition.split('d')[1];
  for (var iteration in corgiOutput) {
    // Iterating throught all ID of expermimentation for current iteration of CoRGI
    corgiOutput[iteration].forEach(function(geneID) {
      if (geneID in experimentationsInformations) {
        if (experimentationsInformations[geneID].hasOwnProperty(condition)) {
          // Iterate through nodes of JSON in construction
          experimentationsJson["nodes"].forEach(function(node) {
            if (node["id"].split('#')[1] == conditionNumber + "." + experimentationsInformations[geneID][condition][0] && node['iteration'] == iteration.split("_")[1]) {
              node["mappedData"].push(experimentationsInformations[geneID]);
            };
          });
        };
      };
    });
  };
  return experimentationsJson;
};

/**
 * Calculate a relative value for each node. This value will be used to
 * determine node height in sankey diagram. Relative value is calculated
 * following this formula: (number of occurence mapped on a given node * 100 /
 * number of occurences mapped on current iteration)
 * @param {Object} metadataWholeJson Object storing all informations needed to
 * construct a Sankey diagram
 */
function addRelativeValueForGOParts(metadataWholeJson) {
  // Iterate through all possible parts
  for (var GOPart in metadataWholeJson["sizeOfEachPart"]) {
    // Iterate through all nodes of current part
    metadataWholeJson["graph"][GOPart]["nodes"].forEach(function(node) {
      // Calculate percentage of representation of given node.
      // Save it in node information, rounded at 3 decimals
      node["relativeValue"] = (node["mappedData"].length * 100 / metadataWholeJson["sizeOfEachPart"][GOPart]["iteration" + "_" + node["iteration"]]);
    });
  };
};

/**
 * Object constructed to store experiments through time and associated data
 * needed to construct Sankey diagrams.
 * *Keys*
 * <pre class='json'>
 * {
 *  "graph": {
 *    "cond1": {},
 *    "cond2": {},
 *    "cond3": {},
 *    "cond4": {}
 *  },
 *  "iteration": {},
 *  "sizeOfEachPart": {
 *    "cond1": {},
 *    "cond2": {},
 *    "cond3": {},
 *    "cond4": {}
 *  },
 *  "inputDataset": {
 *    "total": 0,
 *    "cond1": {},
 *    "cond2": {},
 *    "cond3": {},
 *    "cond4": {}
 *  }
 * };
 * </pre>
 * @return {Object} Object constructed to store experiments through time
 */
function experimentsObject() {
  return {
    "graph": {
      "cond1": {},
      "cond2": {},
      "cond3": {},
      "cond4": {}
    },
    "iteration": {},
    "sizeOfEachPart": {
      "cond1": {},
      "cond2": {},
      "cond3": {},
      "cond4": {}
    },
    "inputDataset": {
      "total": 0,
      "cond1": {},
      "cond2": {},
      "cond3": {},
      "cond4": {}
    }
  };
};

/**
 * Object constructed to store genes through time and associated data
 * needed to construct Sankey diagrams.
 * *Keys*
 * <pre class='json'>
 * {
 *  "graph": {
 *     "biological_process": {},
 *     "cellular_component": {},
 *     "molecular_function": {}
 *  },
 * "iteration": {},
 * "sizeOfEachPart": {
 *   "cellular_component": {},
 *   "molecular_function": {},
 *   "biological_process": {}
 * },
 * "inputDataset": {
 *   "total": 0,
 *   "cellular_component": {},
 *   "molecular_function": {},
 *   "biological_process": {}
 * }
 * };
 * </pre>
 * @return {Object} Object constructed to store genes through time
 */
function goObject() {
  return {
    "graph": {
      "biological_process": {},
      "cellular_component": {},
      "molecular_function": {}
    },
    "iteration": {},
    "sizeOfEachPart": {
      "cellular_component": {},
      "molecular_function": {},
      "biological_process": {}
    },
    "inputDataset": {
      "total": 0,
      "cellular_component": {},
      "molecular_function": {},
      "biological_process": {}
    }
  };
};