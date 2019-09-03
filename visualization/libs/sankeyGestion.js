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
 * buildSankey Configuration of Sankey function using API of sankey.js
 * @param  {integer} width Width of browser's window
 * @param  {integer} padding From configuration
 * @param  {array} iteration Array storing all iteration number
 * @return {function} return a configured sankey function
 */
function buildSankey(width, height, padding, iteration, conf) {
  // iteration.lenght is equivalent to iterationMax
  const nWidth = conf["nodeWidth"] * 0.01 * (width - padding * 2) / (iteration.length + 1);
  const sankey = d3.sankey()
    // Add a function to align node on right iteration
    .nodeAlign(d => d.iteration - Number(iteration[0]))
    // Give node width from configuration
    .nodeWidth(nWidth)
    // Give node padding from configuration
    .nodePadding(conf["nodePadding"])
    .iterations(conf["iterations"])
    // Give size of graph from configuration and informations from browser
    .extent([
      [padding, padding],
      [width - padding, height - padding]
    ]);
  // Add a function to get in a easier way nodeID
  sankey.nodeId(d => d.id)
    // Add a function to sort node following order given in excel spreadsheet
    .nodeSort(
      function(a, b) {
        // Split node ID avoiding to sort following iteration number but just following node ID generated from excel spreadsheet
        a = a.id.split('#');
        b = b.id.split('#');
        // Return node ordered using a d3 function
        return d3.ascending(a, b);
      });
  return sankey;
};

/**
 * variableWidthLink This function takes a sankey link object (source and
 * target node) and return a path between them using bezier curves
 * @param  {type} d Link object
 * @return {string} Path with variable width based on bezier curve
 */
function variableWidthLink(d) {
  // Store source in a const to keep inital data unmodified
  const s = d.source;
  // Store target in a const to keep inital data unmodified
  const t = d.target;
  // Calculate source and target height
  const sy = linkHeights(d, d.source, d.source.sourceLinks);
  const ty = linkHeights(d, d.target, d.target.targetLinks);
  // s.x0 is the right side of the source
  // t.x1 is the left side of the target
  const xm = (s.x0 + t.x1) / 2;
  // Generate a d3 path and construct it using line and bezier curves
  const path = d3.path();
  path.moveTo(s.x0, sy[0]);
  // Generate a bezier curve between the two points
  path.bezierCurveTo(xm, sy[0], xm, ty[0], t.x1, ty[0]);
  path.lineTo(t.x1, ty[1]);
  // Generate a bezier curve between the two points
  path.bezierCurveTo(xm, ty[1], xm, sy[1], s.x0, sy[1]);
  path.closePath();

  return path.toString();
};

/**
 * linkHeights Calculate linkHeight using link, nodes and also number of siblings for each nodes implicated in link
 * @param  {[dictionnary]} link link descriptive variables
 * @param  {[dictionnary]} node node descriptive variables
 * @param  {[dictionnary]} siblings dictionnary of all sibling of a given node
 * @return {[type]} Returns y0, y1 for the source side of a link, based on its
 * siblings
 */
function linkHeights(link, node, siblings) {
  // If link has only one sibling, return direcly coordinate of source node
  if (siblings.length == 1) {
    return [node.y0, node.y1];
  }
  var k = (node.y1 - node.y0) / d3.sum(siblings, (l) => l.value);
  var v0 = d3.sum(siblings.filter((l) => l.index < link.index), (l) => l.value);
  var v1 = v0 + link.value;
  // Calculate value of height based on number of siblings and their values. Sum of all those value will be applicated to node's coordinate to determine his height
  return [node.y0 + k * v0, node.y0 + k * v1];
};