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
// Functions needed to construct object needed by d3.js algorithms
//******************************************************************************
// Classical approach to generate links, ,not fitting with requirement because generate path with only horizontal lines
// .attr("d", d3.sankeyLinkHorizontal())
// .attr("stroke-width", d => Math.max(1, d.width))
// Build a map between linked nodes using their ID. A functionnal function, but using last version of Sankey, a similar function is implemented in native. Keep it in case a previous version of sankey is needed.
// Example of call
// metadataJson = constructNodeMap(metadataJson);
/**
 * [OBSOLETE constructNodeMap Build a map between linked nodes using their ID]
 * @param  {[Json object]} jsonData [A Json object used to construct a sankey diagram]
 * @return {[Json object]} [Json Object fitting now requirements for sankey function]
 */
function constructNodeMap(jsonData) {
  var nodeMap = {};
  jsonData.nodes.forEach(function(x) {
    nodeMap[x.id] = x;
  });
  jsonData.edges = jsonData.edges.map(function(x) {
    if (x.value == 0) {
      return {
        source: nodeMap[x.source],
        target: nodeMap[x.target],
        value: 5,
        pred: x.pred
      };
    } else {
      return {
        source: nodeMap[x.source],
        target: nodeMap[x.target],
        value: Math.log(x.value),
        pred: x.pred
      };
    };
  });
  return jsonData;
};



// *****************************************************************************
// JSON parsing
// *****************************************************************************
/**
 * [A function to deep copy JSON object. Work in recursive fashion allowing to be used with every JSON object]
 * @return {[JSON object]} [cloned JSON object]
 */
function extend() {
  for (var i = 1; i < arguments.length; i++)
    for (var key in arguments[i])
      if (arguments[i].hasOwnProperty(key)) {
        if (typeof arguments[0][key] === 'object' &&
          typeof arguments[i][key] === 'object')
          extend(arguments[0][key], arguments[i][key]);
        else
          arguments[0][key] = arguments[i][key];
      }
  return arguments[0];
};

/**
 * addIteration Add iteration in nodes names, allowing to avoid infinite loop in sankey algorithm
 * @param {Object} jsonData Initial JSON from python script
 * @param {Integer} iterationMax Number of iterations
 */
function addIteration(jsonData, iterationMax) {
  jsonData.links.forEach(function(edge) {
    if ((edge.target.indexOf('#') == -1) && (edge.source.indexOf('#') == -1)) {
      edge.source = edge.iteration + "#" + edge.source;
      edge.target = edge.iteration + 1 + "#" + edge.target;
    };
  });
  jsonData.nodes.forEach(function(node) {
    if (node.id.indexOf('#') == -1) {
      for (var i = 0; i < iterationMax + 2; i++) {
        var newNode = JSON.parse(JSON.stringify(node));
        newNode.id = i + "#" + node.id;
        jsonData.nodes.push(newNode);
      };
    };
  });
  return jsonData;
};

/**
 * removeOrphanedNodes Filter JSON object to remove nodes that are not involved in links]
 * @param  {Object} jsonData Initial JSON from python script
 * @return {Object} Filtered JSON object without nodes that are not involved in links
 */
function removeOrphanedNodes(jsonData) {
  jsonData.nodes = jsonData.nodes.filter(orphanedNodes);
  return jsonData;
};

/**
 * [orphanedNodes Function to determine if node is orphaned or not]
 * @param  {[Object]} node [a node object]
 * @return {[boolean]}      [A boolean to answer if node is orphaned or not]
 */
function orphanedNodes(node) {
  if ((node.sourceLinks.length == 0) && (node.targetLinks.length == 0)) {
    return 0;
  } else {
    return 1;
  };
};
/**
 * A function to filter JSON object, removing all nodes and associated links from a given type
 * @param  {Object} GOJson initial JSON object
 * @param  {string} filter_on type of nodes and associated links that need to be removed]
 * @return {[JSON object]} JSON object filtered
 */
function filter(GOJson, filter_on) {
  // Construct an object that will store returning graph object
  var removed = {
    nodes: [],
    links: []
  };
  // Save nodes from original data if they are not kept by the filter
  GOJson.nodes.forEach(function(n) {
    if ((n.type != filter_on) && (n.id != "http://purl.obolibrary.org/obo/go#")) {
      if (n.hasOwnProperty('type')) {
        // Save node if his type is not the one that was given as an argument
        removed.nodes.push(n);
      }
    }
  });
  //	Remove links from data based on availability of nodes
  GOJson.links.forEach(function(n) {
    removed.nodes.forEach(function(m) {
      // If edge links nodes that still exist
      if ((n.target === m.id) || (n.source === m.id) || (n.pred === m.id)) {
        // If edge does not already exist, save it
        if (!removed.links.includes(n)) removed.links.push(n);
      }
    });
  });
  return removed;
};

// Compute relative value for each nodes, allowing to give an height to each nodes
// Example of call: computeRelativeValue(graphJson["graph"][key], graphJson["sizeOfEachPart"]);
function computeRelativeValue(jsonGraph, iterationSize) {
  jsonGraph.nodes.forEach(function(d) {
    if (typeof d.GOPart != "undefined") {
      d.relativeValue = (d.mappedData.length / iterationSize[d.GOPart]["iteration_" + d.iteration]) * 100;
    } else {
      d.relativeValue = (d.mappedData.length / iterationSize[d.cond]["iteration_" + d.iteration]) * 100;
    };
  });
};
/**
 * OBSOLETE getMaxIteration Search for number of iterations from JSON data
 * @param  {array} jsonData initial JSON object
 * @return {integer} Number of iterations
 */
function getMaxIteration(jsonData) {
  var iterationMax = 0;
  jsonData.links.forEach(function(edge) {
    if (edge.iteration > iterationMax) {
      iterationMax = edge.iteration;
    };
  });
  return iterationMax;
};

function splitFollowingChar(char, string) {
  return string.split(char);
}

function copyNode(node) {
  return Object.assign({}, node);
};


//*****************************************************************************
// Gestion of nodes movements
//*****************************************************************************

// Handle with mobility of nodes and associated links
// Example of calls
// .call(d3.drag()
//   .on('start', dragStart)
//   .on('drag', dragMove)
//   .on('end', dragEnd));

// Default node positions
function dragStart(d) {
  if (!d.__x) d.__x = d3.event.x;
  if (!d.__y) d.__y = d3.event.y;
  if (!d.__x0) d.__x0 = d.x0;
  if (!d.__y0) d.__y0 = d.y0;
  if (!d.__x1) d.__x1 = d.x1;
  if (!d.__y1) d.__y1 = d.y1;
};

function dragMove(d) {
  d3.select(this)
    .attr('transform', function(d) {
      const dx = d3.event.x - d.__x;
      const dy = d3.event.y - d.__y;
      d.x0 = d.__x0 + dx;
      d.x1 = d.__x1 + dx;
      d.y0 = d.__y0 + dy;
      d.y1 = d.__y1 + dy;
      if (d.x0 < 0) {
        d.x0 = 0;
        d.x1 = sankey.nodeWidth();
      }
      if (d.x1 > width) {
        d.x0 = width - sankey.nodeWidth();
        d.x1 = width;
      }
      if (d.y0 < 0) {
        d.y0 = 0;
        d.y1 = d.__y1 - d.__y0;
      }
      if (d.y1 > height) {
        d.y0 = height - (d.__y1 - d.__y0);
        d.y1 = height;
      }
      return `translate(${d.x0}, ${d.y0})`;
    })
  sankey.update(GOData);
  link.attr("d", d => variableWidthLink(d));
};

function dragEnd(d) {
  delete d.__x;
  delete d.__y;
  delete d.__x0;
  delete d.__x1;
  delete d.__y0;
  delete d.__y1;
};

//******************************************************************************
// Construct of d3.js objects in SVG
//******************************************************************************
/**
 * nodeClicked Display some informations of a clicked node into a tooltip
 * @param  {D3 data object} d Data of clicked node
 * @param  {JSON object} GOData Data loaded form local Json
 * @param  {string} typeOfChart Text depend of chart type (Sankey or force
 * directed graph), please give 'forceDirected' or 'sankey']
 */
function nodeClicked(d, GOData, typeOfChart, id) {
  var chart = d3.select("#" + id)
  // Get tooltip container from SVG
  var tooltip = chart.selectAll('.tooltip')
  // If not empty, empty it
  if (tooltip) tooltip.remove();
  // Append a container and place it following node position
  tooltip = chart.append("g")
    .classed("column-labels", true)
    .on("click", function() {
      tooltip.remove()
    });
  if (typeOfChart == 'forceDirected') {
    tooltip.attr("transform", "translate(" + d.x + "," + d.y + ")")
    fillTooltipForceDirectedGraph(d, GOData, tooltip);
  } else {
    tooltip.attr("transform", "translate(" + d.x0 + "," + d.y0 + ")")
    fillTooltipSankey(d, GOData, tooltip);
  };
};

function fillTooltipSankey(d, GOData, tooltip) {
  var rect = tooltip.append("rect")
    .style("fill", "white")
    .style("stroke", "steelblue");

  tooltip.append("text")
    .text("Name: " + d.id)
    .attr("dy", "1em")
    .attr("x", 5);

  tooltip.append("text")
    .text("Label: " + d.lbl)
    .attr("dy", "2em")
    .attr("x", 5);

  if (d.mappedData.length > 0) {
    tooltip.append("text")
      .text("Number of mapped experiments: " + d.mappedData.length)
      .attr("dy", "4em")
      .attr("x", 5);
    tooltip.append("text")
      .text("Mapped experiment:")
      .attr("dy", "5em")
      .attr("x", 5);
    for (var i = 0; i < d.mappedData.length; i++) {
      tooltip.append("text")
        .text(d.mappedData[i].experimentationID)
        .attr("dy", i + 6 + "em")
        .attr("x", 5);
      if (i >= 5) {
        break;
      }
    }
  } else {
    tooltip.append("text")
      .text("No mapped experiment")
      .attr("dy", "4em")
      .attr("x", 5);
  };
  var bbox = tooltip.node().getBBox();
  rect.attr("width", bbox.width + 5)
    .attr("height", bbox.height + 5);
};

function fillTooltipForceDirectedGraph(d, GOData, tooltip) {
  var rect = tooltip.append("rect")
    .style("fill", "white")
    .style("stroke", "steelblue");

  tooltip.append("text")
    .text("Name: " + d.id)
    .attr("dy", "1em")
    .attr("x", 5);

  tooltip.append("text")
    .text("Label: " + d.lbl)
    .attr("dy", "2em")
    .attr("x", 5);

  var connection = GOData.links
    .filter(function(d1) {
      return d1.source.id === d.id;
    })
    .map(function(d1) {
      return d1.target.lbl + " with a weight of " + d1.value;
    })
  tooltip.append("text")
    .text("Connected to: " + connection.join("\n"))
    .attr("dy", "3em")
    .attr("x", 5);

  if (d.mappedGenes.length > 0) {
    tooltip.append("text")
      .text("Number of mapped genes: " + d.mappedGenes.length)
      .attr("dy", "4em")
      .attr("x", 5);
    tooltip.append("text")
      .text("Mapped genes:")
      .attr("dy", "5em")
      .attr("x", 5);
    for (var i = 0; i < 5; i++) {
      tooltip.append("text")
        .text(d.mappedGenes[i].GO_ID)
        .attr("dy", i + 6 + "em")
        .attr("x", 5);
    }
  } else {
    tooltip.append("text")
      .text("No mapped genes")
      .attr("dy", "4em")
      .attr("x", 5);
  };
  var bbox = tooltip.node().getBBox();
  rect.attr("width", bbox.width + 5)
    .attr("height", bbox.height + 5);

};