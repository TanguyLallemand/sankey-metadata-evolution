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
 * getIterationMap Create a sorted map of all iterations for each constructed graph
 * @param  {Object} JSONData A Json object gathering all nodes and associated links for a graph
 * @return {array} sorted array of all iteration numbers
 */
function getIterationMap(JSONData) {
  return [...new Set(JSONData.nodes.map((n) => n.iteration))].sort();
};