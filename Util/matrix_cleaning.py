import numpy as np

"""
Author: Ian Char

Util functions for cleaning matrices. 
"""

"""
Looks through the matrix and will remove any column that has more missing
values than the tolerance provided where the tolerance is the percent of
overall values.

Returns an updated matrix and an updated dictionary
"""
def removeSparseAttributes(mat, dic, tolerance = 0.8):
    rows, cols = mat.shape

    # Find which attributes meet the minimum threshold
    colsToInclude = []
    for c in range(cols):
        accFunc = lambda prev, curr: prev if np.isnan(curr) else 1 + prev
        if reduce(accFunc, mat[:,c], 0)/rows >= tolerance:
            colsToInclude.append(c)

    # Create a new matrix and dictionary
    newMat = np.empty((rows, len(colsToInclude)))
    newDic = {}

    currCol = 0
    for c in colsToInclude:
        newMat[:,currCol] = mat[:, c]
        newDic[currCol] = dic[c]

    return newMat, newDic

def smoothMatrix(mat, smoothFunc):
    print "Not yet implemented"

def normalize(mat, normalizeFunc):
    print "Not yet implemented"
