/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */
function getSizeOfIterations(corgiOutput, metadataWholeJsonIteration) {
  for (var iteration in corgiOutput) {
    metadataWholeJsonIteration[iteration] = corgiOutput[iteration].length;
  };
};

function resetIterationsCounts(metadataWholeJsonIteration) {
  for (var iteration in metadataWholeJsonIteration) {
    metadataWholeJsonIteration[iteration] = 0;
  };
};

function getSizeOfGenesIterations(geneJson, iterations) {
  geneJson["nodes"].forEach(function(node) {
    if (iterations.hasOwnProperty("iteration_" + node.iteration)) {
      iterations["iteration_" + node.iteration] += node.mappedData.length;
    } else {
      iterations["iteration_" + node.iteration] = 0;
    };
  });
};

function createNodes(template, iteration) {
  var nodeDictionnary = {
    "nodes": [],
    "links": []
  };
  for (var iterator in iteration) {
    template.forEach(function(node) {
      var newNode = JSON.parse(JSON.stringify(node));
      // Generate a correct ID making an ID like next example:
      // currentIterationNumber#GOid
      newNode["id"] = iterator.split("_")[1] + "#" + newNode["id"];
      // Add iteration
      newNode["iteration"] = iterator.split("_")[1];
      // Append it in dictionnary
      nodeDictionnary["nodes"].push(newNode);
    });
  };
  return nodeDictionnary;
};

function getSizeOfEachPart(metadataWholeJson) {
  // For each part of GO calculate how many genes are mapped on each GOSlim term at each iterations.

  for (var GOPart in metadataWholeJson["graph"]) {
    if (metadataWholeJson["graph"][GOPart].hasOwnProperty("nodes")) {
      metadataWholeJson["graph"][GOPart]["nodes"].forEach(function(node) {
        metadataWholeJson["sizeOfEachPart"][GOPart]["iteration" + "_" + node["iteration"]] = 0;
      });
      metadataWholeJson["graph"][GOPart]["nodes"].forEach(function(node) {
        metadataWholeJson["sizeOfEachPart"][GOPart]["iteration" + "_" + node["iteration"]] += node["mappedData"].length;
      });
    };
  };
};

function purgeEmptyNodes(genesJson) {
  genesJson["nodes"].forEach(function(node) {
    if (node["mappedData"].length == 0) {
      var index = genesJson["nodes"].indexOf(node);
      if (index > -1) {
        genesJson["nodes"].splice(index, 1);
      };
    };
  });
};

function addEdges(genesJson) {
  // Add edges between nodes if necessary. This means if:
  //   - Iteration of source node is lower than target node
  //   - If source and target ndoes have mappedDatas
  //   - If names are the same
  //
  // Parameters
  // ----------
  // jsonFile : array of dictionnaries
  //     Array gathering all nodes of graph
  //
  // Returns
  // -------
  // array of dictionnary
  //     array gathering all links objects
  //
  // Iterate through nodes of JSON in construction
  genesJson["nodes"].forEach(function(node) {
    // Split node ID
    var nodeSplitted = node["id"].split('#');
    // Get a second node
    genesJson["nodes"].forEach(function(secondNode) {
      // Split node ID
      var secondNodeSplitted = secondNode["id"].split('#');

      // Add edges between nodes if necessary. This means if:
      // - Iteration of source node is lower than target node
      // - If source and target ndoes have mappedDatas
      // - If names are the same
      if (parseInt(nodeSplitted[0]) == parseInt(secondNodeSplitted[0]) + 1) {
        if (node["mappedData"].length > 0 && secondNode["mappedData"].length > 0 && nodeSplitted[1] == secondNodeSplitted[1]) {
          // Construct link
          var edge = {
            "source": node["id"],
            "target": secondNode["id"],
            "pred": "to_change",
            "value": "1",
            "iteration": nodeSplitted[0]
          };
          genesJson["links"].push(edge);
        };
      };
    });
  });
};


function getAllNodesFromInput(genesJson, inputStats, accession) {
  genesJson["nodes"].forEach(function(node) {
    // If node is from input
    if (node["iteration"] == "0") {
      // Construct a new key in inputDataset dictionnary using GOPart name or condition name (this is determined using accession string). Add as value, number of occurence in node
      inputStats[node[accession]][node["lbl"]] = node["mappedData"].length;
      inputStats["total"] += node["mappedData"].length;
    };
  });
};