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
        if reduce(accFunc, mat[:,c], 0)/float(rows) >= tolerance:
            colsToInclude.append(c)

    # Create a new matrix and dictionary 
    if len(colsToInclude) == 0:
        raise RuntimeError("Removing sparse attributes removes all elements")
    newMat = np.asmatrix(np.empty((rows, len(colsToInclude))))
    newDic = {}

    currCol = 0
    for c in colsToInclude:
        newMat[:,currCol] = mat[:, c]
        newDic[currCol] = dic[c]
        currCol += 1

    return newMat, newDic

"""
Smooths each column of the matrix to your specification. The smooth function
passed in should take a numpy column vector as an argument.

The return is the matrix you passed in. THE MATRIX YOU PASS IN WILL BE CHANGED!
"""
def smoothMatrix(mat, smoothFunc):
    rows, cols = mat.shape
    for c in range(cols):
        smoothFunc(mat[:,c])
    return mat

def normalize(mat, normalizeFunc):
    print "Not yet implemented"


"""HELPER HIGHER ORDER FUNCTIONS"""

""" Smoothing functions """

"""
Replace every NaN with some number, call this function to get the function
to be passed to smoothMatrix.
"""
def smoothByReplacement(valToReplace):
    def changeToValue(vect):
        rows = vect.shape[0]
        for r in range(rows):
            if np.isnan(vect[r]):
                vect[r] = valToReplace
    return changeToValue

def smoothByAverage(vect):
    rows = vect.shape[0]
    
    valToReplace = 0
    
    # Find average
    accFunc = lambda prev, curr: prev if np.isnan(curr) else curr + prev
    countFunc = lambda prev, curr: prev if np.isnan(curr) else 1 + prev
    toDivide = reduce(countFunc, vect, 0.0)
    if toDivide != 0:
        valToReplace =  reduce(accFunc, vect, 0.0)/toDivide

    # Replace
    for r in range(rows):
        if np.isnan(vect[r]):
            vect[r] = valToReplace

if __name__ == '__main__':
    testMat = np.matrix([[np.NAN, 2, 3, 4],
                        [np.NAN, 2, 8, 3],
                        [np.NAN, np.NAN, 5, 5],
                        [np.NAN, np.NAN, 2, 3],
                        [np.NAN, 2, np.NAN, 5]])
    testDict = {0:"A", 1:"B", 2:"C", 3:"D"}
    print "----------- Test Matrix -----------"
    print testMat
    print testDict
    print "----------- removeSparseAttributes -----------"
    print removeSparseAttributes(testMat, testDict)
    print "----------- smoothByReplacement(0)------------"
    print smoothMatrix(np.copy(testMat), smoothByReplacement(0))
    print "----------- smoothByAverage ------------------"
    print smoothMatrix(np.copy(testMat), smoothByAverage)
