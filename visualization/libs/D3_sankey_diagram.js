/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */
function generateSankeyDiagram(confJson, graphJson, fisherDataset, corgi) {
  //****************************************************************************
  // Initialize some variables, get some config variables from config file
  //****************************************************************************
  // Get some values form config files
  var numberOfGraph = confJson["SVG"]["numberOfGraph"];
  var margins = {
    top: confJson["SVG"]["margins"]["top"],
    right: confJson["SVG"]["margins"]["right"],
    bottom: confJson["SVG"]["margins"]["bottom"],
    left: confJson["SVG"]["margins"]["left"]
  };
  var padding = confJson["SVG"]["padding"];
  var formatNumber = d3.format(confJson["stat"]["formatNumber"]);
  // Get browser size and store in an object
  var size = getSize();
  var width = (size.width - margins.right - margins.left) / numberOfGraph;
  var height = size.height / numberOfGraph;
  // Set up the colour scale
  var color = d3.scaleOrdinal(d3.schemeAccent);
  //****************************************************************************
  // Parse data
  //****************************************************************************
  // Iterate trought JSON to select data of a graph
  for (var key in graphJson["graph"]) {
    // If a graph has empty links or empty nodes pass it
    if (graphJson["graph"][key].links.length == 0 || graphJson["graph"][key].nodes.length == 0) {
      continue;
    };
    // Open an SVG to construct current graph in it
    var svg = openSVGRoot(width, height, margins, key, numberOfGraph);
    // Append a container to handle with all chart elements
    var container = svg.append('g')
      .attr("class", "container")
      // Call zoom for SVG container.
      .call(d3.zoom()
        .on('zoom', zooming));
    // Open a chart container and place it
    var chart = container.append("g")
      .attr("align", "center")
      .attr("transform", "translate(" + margins.left + "," + margins.top + ")");
    // Get all possible iteration for current graph
    var iterationArray = getIterationMap(graphJson["graph"][key]);
    // Generate a sankey function fitting with requirement for current graph
    sankey = buildSankey(width, height, padding, iterationArray, confJson["sankey"]);
    // Initialize sankey diagramm, add nodes and links map
    const {
      nodes,
      links
    } = sankey({
      nodes: graphJson["graph"][key].nodes.map(d => Object.assign({}, d)),
      links: graphJson["graph"][key].links.map(d => Object.assign({}, d))
    });
    graphJson["graph"][key].nodes = nodes;
    graphJson["graph"][key].links = links;
    // Compute a two-tailed fisher exact test in his non-central variant. P-value of each nodes is saved in their object
    computeFisherOnEachNodes(graphJson["graph"][key], graphJson.iteration, fisherDataset, graphJson["inputDataset"]);
    //**************************************************************************
    // Draw links and node following Sankey layout
    //**************************************************************************
    // Add links to SVG, but without position them
    var link = generateSVGLinks(chart, graphJson["graph"][key], formatNumber, confJson);
    // Add in nodes to chart container
    var node = generateSVGNodes(chart, graphJson["graph"][key], iterationArray, color, width, height, margins, formatNumber, size.width, confJson);
    // Add a label to each iteration
    generateIterationLabelsAndTitle(chart, iterationArray, graphJson["graph"][key], margins, width, height, key, corgi);
  };
};