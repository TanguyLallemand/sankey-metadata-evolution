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
 * getSize Get size of window used to display graphs
 * @return {Object} A dictionnary with two keys, width and height of
 * current window
 */
function getSize() {
  var width = 0,
    height = 0;
  if (typeof(window.innerWidth) == 'number') {
    // Non-IE compatible
    width = window.innerWidth;
    height = window.innerHeight;
  } else if (document.documentElement && (document.documentElement.clientWidth || document.documentElement.clientHeight)) {
    // IE 6+ in 'standards compliant mode'
    width = document.documentElement.clientWidth;
    height = document.documentElement.clientHeight;
  } else if (document.body && (document.body.clientWidth || document.body.clientHeight)) {
    // IE 4 compatible
    width = document.body.clientWidth;
    height = document.body.clientHeight;
  }
  return {
    "height": height,
    "width": width
  };
};
/**
 * Open a new SVG root tro construct a new sankey diagramm
 * @param  {Integer} width Needed width of SVG graph
 * @param  {Integer} height Needed height of SVG graph
 * @param  {Object} margins All margins size in an object
 * @param  {String} key Uniq string allowing to give a unqi id to each graph,
 * allowing to d3.select it easly
 * @return {Object} SVG object stroring a root
 */
function openSVGRoot(width, height, margins, key) {
  // Append the svg canva to the page
  var svg = d3.select("#chart")
    .append("svg")
    .attr("id", key)
    // Set right dimensions
    .attr("width", width + margins.left + margins.right)
    .attr("height", height + margins.top + margins.bottom);
  return svg;
};


/**
 * [zooming translates the size of the svg container]
 */
function zooming() {
  d3.selectAll('svg').attr("transform", "translate(" + d3.event.transform.x + ", " + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
};

/**
 * columnLabelPosition A function to detect where nodes are positionned allowing to put axis label at right places
 * @param  {array} iteration Array storing all iterations number for current
 * graph
 * @param  {array of nodes} nodes Array of all nodes of current graph
 * @return {float} Center of a given for each iteration node
 */
function columnLabelPosition(iteration, nodes, margins) {
  let nodesAtDepth = nodes.filter(n => n.iteration === iteration);
  let x0 = d3.min(nodesAtDepth, n => n.x0);
  let x1 = d3.min(nodesAtDepth, n => n.x1);
  return ((x0 + x1) / 2) - margins.left;
};

//******************************************************************************
// Shape gestion
//******************************************************************************

/**
 * * This function allows to construct all links in SVG format based on links
 * array computed by Sankey algorithm
 * @param  {Object} chart SVG object containning chart in construction
 * @param  {Object} GOData Object containning in node-link format every graph
 * informations.
 * @param  {String} formatNumber String of how many decimals are kept when
 * rounding
 * @param  {Object} confJson A Json used to hold some configuration variables
 * @return {Object} SVG object containning all links in SVG format
 */
function generateSVGLinks(chart, GOData, formatNumber, confJson) {
  var link = chart.append("g")
    .selectAll(".link")
    .data(GOData.links)
    .enter()
    .append("path")
    .attr("class", "link")
    // Add a path with variable width
    .attr("d", d => variableWidthLink(d))
    // Add color of links if p-value of exact fisher test against input is under a threshold and if target relative value is greater than source's
    .style("fill", function(d) {
      if (d.target.pValueAgainstInput < confJson["stat"]["threshold"] && (d.target.relativeValue < d.source.relativeValue)) {
        return confJson["graph"]["linkColors"]["significative"];
      } else {
        return confJson["graph"]["linkColors"]["nonSignificative"];
      };
    })
    .style("stroke", function(d) {
      return d3.rgb(d.color).darker(2);
    })
    .style("opacity", 0.8)
    .on('mouseover', function() {
      d3.select(this).style("opacity", 0.5);
    })
    .on('mouseout', function() {
      d3.select(this).style("opacity", 0.8);
    });

  // Add the link titles
  link.append("title")
    .text(function(d) {
      return generateTitle(d, "link", formatNumber);
    });
  return link;
};

/**
 * This function allows to construct all nodes in SVG format based on nodes
 * array computed by Sankey algorithm
 * @param  {Object} chart SVG object containning chart in construction
 * @param  {Array} iterationArray An array containning iteration number
 * @param  {Object} GOData Object containning in node-link format every graph
 * informations.
 * @param  {Array} color Array of colors in hexadecimale format
 * @param  {object} margins margins size
 * @param  {integer} width width size of chart
 * @param  {integer} height height size of chart
 * @param  {String} formatNumber String of how many decimals are kept when
 * rounding
 * @param  {integer} forceDirectedGraphWidth width size of force directed chart
 * @param  {Object} confJson A Json used to hold some configuration variables
 * @return {Object} SVG object containning all nodes in SVG format
 */
function generateSVGNodes(chart, GOData, iterationArray, color, width, height, margins, formatNumber, forceDirectedGraphWidth, confJson) {

  var node = chart.append("g")
    .selectAll(".node")
    .data(GOData.nodes)
    .enter()
    .append("g")
    .attr("class", "node")
    // Place node in SVG
    .attr("transform", function(d) {
      return "translate(" + d.x0 + "," + d.y0 + ")";
    });
  // Add the rectangles for the nodes
  node.append("rect")
    .attr("height", function(d) {
      return d.y1 - d.y0;
    })
    .attr("width", sankey.nodeWidth())
    // Color nodes following their label
    .style("fill", function(d) {
      return d.color = color(d.lbl.replace(/ .*/, ""));
    })
    .style("opacity", function(d) {
      if (parseFloat(d.pValue) < parseFloat(confJson["stat"]["threshold"])) {
        return confJson["graph"]["nodeOpacity"]["significative"];
      } else {
        return confJson["graph"]["nodeOpacity"]["nonSignificative"];
      };
    })
    // Add a frame to rectangle a little more darker
    .style("stroke", function(d) {
      return d3.rgb(d.color).darker(2);
    })
    // Add a title to each nodes
    .append("title")
    .text(function(d) {
      return generateTitle(d, "node", formatNumber);
    });

  node.on("click", function(d) {
    deployForceDirectedGraph(d.id, forceDirectedGraphWidth, 600, confJson);
  })


  // Add in the title for the nodes
  node.append("text")
    // Give an x coordinate for label placement
    .attr("x", function(d) {
      // Put label a the right place if it belong to first iteration
      if (d.iteration == iterationArray[0]) {
        return -100 + sankey.nodeWidth();
      };
      // Put label a the right place if it belong to last iteration
      if (d.iteration == iterationArray[iterationArray.length - 1]) {
        return 8 + sankey.nodeWidth();
      };
    })
    // Place label on center of node
    .attr("dy", function(d) {
      return (d.y1 - d.y0) / 2;
    })
    // Place label on right or left side of node following his place in diagram
    // .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
    .attr("text-anchor", "start")
    .attr("font-size", "0.8em")
    // If the position of the node on the x axis is less than half the width, the title is placed on the right of the node and anchored at the start of the text
    .text(function(d) {
      // If node belong to first or last iteration, add a label, else don't add it. This allow to add less text to graph and make a more easy reading
      // For display label at beginning and end :  if ((d.iteration == iterationArray[0] || d.iteration == iterationArray[iterationArray.length - 1]) && parseFloat(d.pValue) < parseFloat(confJson["stat"]["threshold"])) {
      if (d.iteration == iterationArray[iterationArray.length - 1] && parseFloat(d.pValue) < parseFloat(confJson["stat"]["threshold"])) {
        return d.lbl;
      };
    });
  return node;
};

/**
 * Generate for a given chart titles:
 * * Of Y axe
 * * Of X axe
 * @param  {object} chart SVG object to add in it text elements
 * @param  {Array} iterationArray An array containning iteration number
 * @param  {Object} GOData Object containning in node-link format every graph inforamtions. Allows to get coordinates of a given node
 * @param  {object} margins margins size
 * @param  {integer} width width size of chart
 * @param  {integer} height height size of chart
 * @param  {string} title string title of y axe
 * @param  {Object} corgiOutput Object gathering list of gene or experiments
 * for each iteration of CoRGI
 * @return {Object} SVG object of graph with title added
 */
function generateIterationLabelsAndTitle(chart, iterationArray, GOData, margins, width, height, title, corgiOutput) {
  chart.append("g")
    .classed("column-labels", true)
    .attr("transform", `translate(${margins.left}, 0)`)
    .selectAll("text.column-label")
    .data(iterationArray)
    .join("text")
    .classed("column-label", true)
    .attr("x", d => columnLabelPosition(d, GOData.nodes, margins))
    .attr("y", margins.top - 70)
    .attr("text-anchor", "middle")
    .attr("font-size", "0.8em")
    .text(function(d) {
      if (d != 0) {
        return "It " + d;
      } else {
        return "Input";
      }
    });

  chart.append("g")
    .classed("column-labels", true)
    .attr("transform", `translate(${margins.left}, 0)`)
    .selectAll("text.column-label")
    .data(iterationArray)
    .join("text")
    .classed("column-label", true)
    .attr("x", d => columnLabelPosition(d, GOData.nodes, margins))
    .attr("y", margins.top - 50)
    .attr("text-anchor", "middle")
    .attr("font-size", "0.8em")
    .text(function(d) {
      if (d != 0) {
        return corgiOutput["iteration_" + d].length;
      } else {
        return corgiOutput["iteration_" + d].length;
      }
    });
  // TODO: Improve this quick and dirty patch
  if (title == "cond2") {
    title = "Organ";
  } else if (title == "cond3") {
    title = "Biological Insight";
  } else if (title == "cond4") {
    title = "Background";
  };

  chart.append("g")
    .append("text")
    .attr("transform", "rotate(-90)")
    .attr("y", 0 - 25)
    .attr("x", 0 - (height / 2))
    .attr("dy", "1em")
    .style("text-anchor", "middle")
    .text(title);

};


function generateTitle(d, type, formatNumber) {
  if (type == "node") {
    if (d.hasOwnProperty('pValueAgainstInput')) {
      return d.lbl + "\n" + "Valeur relative: " + formatNumber(d.relativeValue) + "%" + "\n" + "Number of associated elements: " + d.mappedData.length + "\n" + "p-value associated with the exact Fisher test against the TAIR data set: " + formatNumber(d.pValue) + "\n" + "p-value associated with the exact Fisher test against the input dataset: " + formatNumber(d.pValueAgainstInput);
    } else {
      return d.lbl + "\n" + "Valeur relative: " + formatNumber(d.relativeValue) + "%" + "\n" + "Number of associated elements: " + d.mappedData.length + "\n" + "p-value associated with the exact Fisher test against the TAIR data set: " + formatNumber(d.pValue);
    };
  } else {
    return d.source.lbl + " → " +
      d.target.lbl + "\n" +
      "Number of associated elements: " + d.source.mappedData.length + "(" + formatNumber(d.source.relativeValue) + "%)" + " → " + d.target.mappedData.length + "(" + formatNumber(d.target.relativeValue) + "%)" + "\n";
  };
};