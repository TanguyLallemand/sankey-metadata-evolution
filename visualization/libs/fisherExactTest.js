/* ************************************************************************
  CoRGI : The Co-Regulated Gene Investigator

  Copyright: 2019 INRA http://www.inra.fr

  License:
    CeCILL: http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
    See the LICENCE file in the project's top-level directory for details.

  Author:
    * Tanguy LALLEMAND, BIDEFI team, IRHS
************************************************************************ */

// The Fisher exact Test is a statistical test used to compare two proportions. This test is generally used with low manpower but is valid for all sample sizes. It is a test qualified as exact because the probabilities can be calculated exactly rather than relying on an approximation that only becomes correct asymptotically as in the chi2 test.
// In the exact Fisher test, the null hypothesis is that there is no enrichment between the variables studied. When using this test with high numbers (such as the number of genes in the human genome or the number of categories available in Gene Ontology), it is quite common to find small enrichments designated as very significant. In these cases, the test result becomes very difficult to interpret. Indeed, what to do with a 2% enrichment returning a p-value of 0.0001?
// There is a variant of the test that changes the null hypothesis by assuming that the enrichment is smaller than a given value. This variant is called non central



/**
 * computeFisherOnEachNodes Compute a non central fisher exact test for each nodes of graph and add associated p-value in nodes object
 * @param  {dictionnary} GOData dictionnary storing graph nodes and their associated links
 * @param  {dictionnary} iterationObject dictionnary storing size of each iterations
 * @param  {dictionnary} TAIRDataSet        dictionnary gathering count of occurence for each element
 */
function computeFisherOnEachNodes(GOData, iterationObject, TAIRDataSet, inputDataset) {
  // Iterate on all nodes of graph
  GOData.nodes.forEach(function(d) {
    // Fisher exact test using current iteration against TAIR data set
    // Construct following 2*2 contingency table:
    // n11  n12   n
    // n21  n22
    // m1   m2

    // Number of mapped      Number of mapped   Total of line
    // data on               data on
    // current term          current term in TAIR
    //
    // Number of mapped      Number of mapped
    // data on               data on
    // current iteration     TAIR data set
    // Total of column       Total of column
    var n11 = d.mappedData.length;
    var n12 = TAIRDataSet[d.lbl];
    var n21 = iterationObject["iteration_" + d.iteration] - n11;
    var n22 = TAIRDataSet["total"] - n12;

    // Compute p-value of exact Fisher test using current iteration and TAIR dataset
    // Store p-value in node object
    d.pValue = exact_nc(n11, n12, n21, n22, 1);

    // Fisher exact test using current iteration against input data set
    if (d.iteration != 0) {
      var n11 = d.mappedData.length;
      var n21 = iterationObject["iteration_" + d.iteration] - n11;
      if (d.hasOwnProperty("GOPart")) {
        var n12 = inputDataset[d.GOPart][d.lbl];
      } else if (d.hasOwnProperty("cond")) {
        var n12 = inputDataset[d.cond][d.lbl];
      };
      var n22 = inputDataset["total"] - n12;
      // Store p-value in node object
      d.pValueAgainstInput = exact_nc(n11, n12, n21, n22, 1);
    };
  });
};


/**
 * lngamm Difficultiy to calcul exact value due to high factorial values. A better approach is based on a gamma function or a log-gamma function. Use log-probabilities to avoid manipulating small numbers which could produce an underflow.
 * @param  {Float} z Input float
 * @return {Float}   Log of input value
 */
function lngamm(z) {
  // Reference: "Lanczos, C. 'A precision approximation
  // of the gamma function', J. SIAM Numer. Anal., B, 1, 86-96, 1964."
  // Translation of Alan Miller's FORTRAN-implementation
  // See http://lib.stat.cmu.edu/apstat/245
  var x = 0;
  x += 0.1659470187408462e-06 / (z + 7);
  x += 0.9934937113930748e-05 / (z + 6);
  x -= 0.1385710331296526 / (z + 5);
  x += 12.50734324009056 / (z + 4);
  x -= 176.6150291498386 / (z + 3);
  x += 771.3234287757674 / (z + 2);
  x -= 1259.139216722289 / (z + 1);
  x += 676.5203681218835 / (z);
  x += 0.9999999999995183;
  return (Math.log(x) - 5.58106146679532777 - z + (z - 0.5) * Math.log(z + 6.5));
};

function lnfact(n) {
  if (n <= 1) return (0);
  return (lngamm(n + 1));
};

/**
 * lnbico ln of the binomial coefficient
 * @param  {integer} n total of first line of contingency table
 * @param  {integer} k number of
 * @return {float}   the log of the number of possible combinations to choose k
 * in n
 */
function lnbico(n, k) {
  return (lnfact(n) - lnfact(k) - lnfact(n - k));
};


// Construct following 2*2 contingency table:
// n11  n12   n
// n21  n22
// m1   m2

// Number of mapped      Number of mapped   Total of line
// data on               data on
// current term          current term
//
// Number of mapped      Number of mapped
// data on               data on
// current iteration     TAIR data set
// Total of column       Total of column
//
/**
 * exact_nc This function is used for comput non central Fisher Exact test
 * .Deciding on an x allows you to fill the table using the totals. The p-value
 * of the exact Fisher test is then calculated by adding the probabilities for
 * the scenario where x is greater than the observed value n11. This is kept in
 * "den_sum" and is calculated by the last "for" loop of the function. Note
 * that all sums come from adjusted probabilities ( - max_l in log space). This
 * avoids adding up very small numbers, which could lead to underflow. Since
 * the final p-value is the result of a ratio, the adjustment factor cancels
 * itself out in Math.exp (den_sum - sum_l). Finally, "w" is used to pass the
 * threshold required for the odds ratio (ω).
 * @param  {integer} n11 Cell at the top left corner of the contingency table,
 * gather number of mapped data on current term in CoRGI dataset for current
 * iteration
 * @param  {integer} n12 Cell at the top right corner of the contingency table,
 * gather number of mapped data on current term in TAIR/input dataset
 * @param  {integer} n21 Cell at the bottom left corner of the contingency
 * table, gather number of mapped data in CoRGI dataset for current
 * iteration
 * @param  {integer} n22 Cell at the bottom RIGHT corner of the contingency
 * table, gather number of mapped data on tair dataset
 * @param  {float} w Threshold required for the odds ratio (ω).
 * @return {float} P-value associated to non central Fisher exact test.
 */
function exact_nc(n11, n12, n21, n22, w) {
  // Calculation of missing data to fully complete the contingency table
  // Number of occurence of current element in current iteration
  // For example:
  // Chloroplast at iteration 0 appear 612 times
  var x = n11;
  // Total of occurences of current term in bot data sets
  // Chloroplast:
  // 612+434=1046
  var m1 = n11 + n21;
  // Chloroplast:
  // 14886 + 382327 = 397213
  var m2 = n12 + n22;
  // 612 + 14886 = 15498
  var n = n11 + n12;

  var x_min = Math.max(0, n - m2);
  var x_max = Math.min(n, m1);
  var l = [];

  for (var y = x_min; y <= x_max; y++) {
    l[y - x_min] = (lnbico(m1, y) + lnbico(m2, n - y) + y * Math.log(w));
  }
  var max_l = Math.max.apply(Math, l);

  var sum_l = l.map(function(x) {
    return Math.exp(x - max_l);
  }).reduce(function(a, b) {
    return a + b;
  }, 0);
  sum_l = Math.log(sum_l);

  var den_sum = 0;
  for (var y = x; y <= x_max; y++) {
    den_sum += Math.exp(l[y - x_min] - max_l);
  }
  den_sum = Math.log(den_sum);
  // Calcul are carried in log, the adjustment factor cancels itself out using exponnentials
  return Math.exp(den_sum - sum_l);
};