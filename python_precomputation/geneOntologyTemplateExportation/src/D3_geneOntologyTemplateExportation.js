// Set the sankey diagram properties
var sankey = d3.sankey()
  .nodeWidth(36)
  .nodePadding(5)
  .iterations(16);

// Load data from local Json file
d3.json("../../data/output/goslim_plant.json").then(function(GOData) {
  // Set filter
  var filter_on = "PROPERTY";
  // Filter data
  GOData = filter(GOData, filter_on);
  // Initialize sankey diagramm
  const {
    nodes,
    links
  } = sankey({
    nodes: GOData.nodes.map(d => Object.assign({}, d)),
    links: GOData.edges.map(d => Object.assign({}, d))
  });
  var extractedNodes = extractNodesOfLastLevel(nodes);
  console.log(extractedNodes);
  var jsonOutputFile = JSON.stringify(extractedNodes);
  //Save the file contents as a DataURI
  var dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(jsonOutputFile);

  //Write it as the href for the link
  var link = document.getElementById('link').href = dataUri;




  function extractNodesOfLastLevel(nodes) {
    var extractedNodes = {
      "nodes": [],
      "links": []
    }
    nodes.forEach(function(node) {
      if (node.targetLinks.length == 0) {
        var extractedNode = {
          "id": node.id,
          "lbl": node.lbl,
          "type": node.type,
          "meta": node.meta,
          "mappedData": []
        }
        extractedNodes.nodes.push(extractedNode);
      };
    });
    return extractedNodes;
  };

  function extractNodesOfAGivenDepth(nodes, depth) {
    var extractedNodes = {
      "nodes": [],
      "links": []
    }
    nodes.forEach(function(node) {
      if (node.depth == depth) {
        extractedNodes.nodes.push(node);
      };
    });
    return extractedNodes;
  };

  function filter(GOJson, filter_on) {
    // Construct an object that will store returning graph object
    var removed = {
      nodes: [],
      edges: []
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
    GOJson.edges.forEach(function(n) {
      removed.nodes.forEach(function(m) {
        // If edge links nodes that still exist
        if ((n.target === m.id) || (n.source === m.id) || (n.pred === m.id)) {
          // If edge does not already exist, save it
          if (!removed.edges.includes(n)) removed.edges.push(n);
        }
      });
    });
    return removed;
  };
});