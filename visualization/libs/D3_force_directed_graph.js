/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */
function deployForceDirectedGraph(nodeName, width, height, confJson) {

  var margins = {
    top: confJson["SVG"]["margins"]["top"],
    right: confJson["SVG"]["margins"]["right"],
    bottom: confJson["SVG"]["margins"]["bottom"],
    left: confJson["SVG"]["margins"]["left"]
  };
  // Set up the colour scale
  var color = d3.scaleOrdinal(d3.schemeAccent);
  //Set
  var radius = confJson["forceDirected"]["nodeRadius"];
  var oldSVG = d3.select("#forceDirectedGraph").remove();
  // Open an SVG to construct current graph in it
  var svg = d3.select("#chart")
    .append("svg")
    .attr("id", "forceDirectedGraph")
    .attr("width", width)
    .attr("height", height);
  // Append a container to handle with all chart elements
  var container = svg.append('g')
    .attr("class", "container")
    // Call zoom for SVG container.
    .call(d3.zoom()
      .on('zoom', zooming));
  // Create form to search for node
  // createForm();

  // Initialize simulation
  var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) {
      return d.id;
    }).distance(confJson["forceDirected"]["distance"]).strength(confJson["forceDirected"]["strength"]))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(40));


  nodeName = nodeName.split('#')
  // d3.json("../../data/GO_rooted_slim_term/GO.json").then(function(GOData) {
  // Load data from local Json file
  d3.json("../../data/GO_rooted_slim_term/" + nodeName[0] + "_" + nodeName[1] +
    ".json").then(function(GOData) {
    // Filter data
    // GOData = filter(GOData, "PROPERTY");
    // Debug
    console.log(GOData);
    var svgElements = constructNodesEdges(GOData);
    var node = svgElements[0];
    var labels = svgElements[1];
    var link = svgElements[2];
    var circles = svgElements[3];
    // Update simulation using data, to give a position to each circle and linked lines
    simulation
      .nodes(GOData.nodes)
      .on("tick", ticked)
      .force("link")
      .links(GOData.links);
    // Allow to keep orphaned nodes at center of graph and avoid them to go in corners. Don t have any effect on linked nodes.
    simulation
      .force("forceX", d3.forceX(width / 2).strength(function(d) {
        return hasLinks(d, GOData.links) ? 0 : 0.05;
      }))
      .force("forceY", d3.forceY(height / 2).strength(function(d) {
        return hasLinks(d, GOData.links) ? 0 : 0.05;
      }));
    // Core of simulation, give a position to each circles and lines, detect collisions
    function ticked() {
      // Variables to calculate collide
      var q = d3.quadtree(node);
      var i = 0;
      var j = 0;
      var n = node.length;
      var m = link.length;
      while (++i < n) q.visit(collide(node[i]));
      while (++j < m) q.visit(collide(link[j]));
      link
        .attr("x1", function(d) {
          return d.source.x;
        })
        .attr("y1", function(d) {
          return d.source.y;
        })
        .attr("x2", function(d) {
          return d.target.x;
        })
        .attr("y2", function(d) {
          return d.target.y;
        });
      // New tick function allowing to bound graph in canva
      circles
        .attr("cx", function(d) {
          return d.x = Math.max(radius, Math.min(width - radius, d.x));
        })
        .attr("cy", function(d) {
          return d.y = Math.max(radius, Math.min(height - radius, d.y));
        });
      // Update the position of the text element
      labels
        //Calculate label's coordinates
        .attr("x", function(d) {
          return d.x;
        })
        .attr("y", function(d) {
          return d.y;
        });
    }

    /**
     * [collide Function to detect collisions of nodes]
     * @param  {[type]} node [node object gathering all spatial informations of a given node and related data]
     * @return {[float]}      [Coordinate of given node]
     */
    function collide(node) {
      var r = node.radius + 30,
        nx1 = node.x - r,
        nx2 = node.x + r,
        ny1 = node.y - r,
        ny2 = node.y + r;
      return function(quad, x1, y1, x2, y2) {
        if (quad.point && (quad.point !== node)) {
          var x = node.x - quad.point.x,
            y = node.y - quad.point.y,
            l = Math.sqrt(x * x + y * y),
            r = node.radius + quad.point.radius;
          if (l < r) {
            l = (l - r) / l * .5;
            node.x -= x *= l;
            node.y -= y *= l;
            quad.point.x += x;
            quad.point.y += y;
          }
        }
        return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
      };
    }


    function hasLinks(d, links) {
      var isLinked = false;
      links.forEach(function(l) {
        if (l.source.id == d.id) {
          isLinked = true;
        }
      })
      return isLinked;
    }
    //**************************************************************************
    // Gestion of movement of nodes
    //**************************************************************************
    /**
     * [dragstarted Modify coordinates of a node that begin to be dragged]
     * @param  {[type]} d [Node data]
     */
    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    /**
     * [dragged Modify coordinates of a node that is dragged]
     * @param  {[type]} d [Node data]
     */
    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }
    /**
     * [dragended Modify coordinates of a node that finish to be dragged]
     * @param  {[type]} d [Node data]
     */
    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    };

    /**
     * [constructNodesEdges Generate all SVG objects for Force directed graph]
     * @param  {[type]} GOData [Dictionnary gathering graph data in Json-LD format. An example:
      * "nodes":[
            { "mappedData": […],
              "lbl": "cytoskeleton",
              "meta": {…},
              "id": "GO:0000166"
            },
          ],
         "links":[
           {
             "source":"GO:0000166","target":"GO:0005856","pred":"is_a"
           }
       ]
     }
    ]
     * @return {[array of [node, labels, link, circles]]} [return all SVG objects generated for Force directed graph]
     */
    function constructNodesEdges(GOData) {
      var link = container.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(GOData.links)
        .enter().append("line")
        // To have a stroke width depending on particular variable, please
        // uncomment following lines
        // .attr("stroke-width", function(d) {
        //   return Math.log(Math.sqrt(d.value));
        // })
        .attr("stroke-width", 2)
        .style("stroke", function(d) {
          return color(d.pred);
        })
        .style("stroke-opacity", 0.6)
        .attr("marker-end", "url(#end)");

      link.append("title")
        .text(function(d) {
          return d.pred;
        })
      // Build the arrow.
      container.append("svg:defs")
        .selectAll("marker")
        .data(["end"]) // Different link/path types can be defined here
        .enter().append("svg:marker") // This section adds in the arrows
        .attr("id", String)
        .style("fill", "#386cb0")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 10)
        .attr("refY", 0)
        .attr("markerWidth", 3)
        .attr("markerHeight", 3)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");

      var node = container.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(GOData.nodes)
        .enter()
        .append("g")

      var circles = node.append("circle")
        .attr("class", "node")
        .attr("r", function(d) {
          if (d.mappedData.length > 0) {
            return Math.log(d.mappedData.length) + radius;
          } else {
            return radius;
          };
        })
        .style("fill", function(d) {
          for (var i = 0; i <= d.meta.basicPropertyValues.length; i++) {
            if ((d.meta.basicPropertyValues[i].val == 'biological_process') || (d.meta.basicPropertyValues[i].val == 'cellular_component') || (d.meta.basicPropertyValues[i].val == 'molecular_function')) {
              return color(d.meta.basicPropertyValues[i].val);
            }
          };
        })
        .style("opacity", function(d) {
          if (d.mappedData.length > 0) {
            return 1;
          } else {
            return 0.55;
          };
        })
        .style("pointer-events", "all")
        .on("click", function(d) {
          nodeClicked(d, GOData, 'forceDirected');
        })
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));

      var labels = node.append("text")
        .text(function(d) {
          return d.lbl;
        })
        .attr("class", "textLabel")
        .attr("dx", 12)
        .attr("dy", ".85em")
        .attr("font-size", "0.8em")
        .style("text-anchor", "middle")
        .style("fill", "#555")
        .style("pointer-events", "none"); // to prevent mouseover/drag capture

      node.append("title")
        .text(function(d) {
          var string = "Number of mapped Genes: " + d.mappedData.length + "\n";
          if (d.mappedData.length >= 1) {
            for (var i = 0; i < d.mappedData.length; i++) {
              string = string + d.mappedData[i].Locus_name + "\n"
              if (i > 4) {
                break;
              }
            };
          };
          return string;
        });
      return [node, labels, link, circles]
    };
  });
};