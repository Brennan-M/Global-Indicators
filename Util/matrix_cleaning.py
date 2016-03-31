import numpy as np

"""
Author: Ian Char

Util functions for cleaning matrices.
"""

"""
Splits the given name of the attribute off from the matrix and returns it as a
vector. Returns a new matrix (old one not altered), new dict (old one not
altered), and the vector of the attribute.
"""
def splitOffAttr(mat, dic, attribute):
    rows, cols = mat.shape

    # Find index in matrix corresponding to attribute
    attrIndex = -1
    for key, val in dic.items():
        if attribute == val:
            attrIndex = key
            break
    if attrIndex < 0:
        raise RuntimeError("Given attribute was not found in the dictionary.")

    # Remove column
    attrVect = mat[:, attrIndex]

    newMat = np.asmatrix(np.empty((rows, cols - 1)))
    newMat[:,:attrIndex] = mat[:,:attrIndex]
    newMat[:,attrIndex:] = mat[:, (attrIndex + 1):]

    newDic = {}
    for key, val in dic.items():
        if key != attrIndex:
            newDic[key if key < attrIndex else key - 1] = val

    return newMat, newDic, attrVect


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
Transforms each column of the matrix to your specification. The function
passed in should take a numpy column vector as an argument.

The return is the matrix you passed in. THE MATRIX YOU PASS IN WILL BE CHANGED!
"""
def transformColumns(mat, colFunc):
    rows, cols = mat.shape
    for c in range(cols):
        colFunc(mat[:,c])
    return mat

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

""" Normalizing functions """
def normalizeByMinMax(vect):
    rows = vect.shape[0]
    minimum, maximum = min(vect), max(vect)
    if maximum - minimum < 10 ** -8:
        for r in range(rows):
            if not np.isnan(vect[r]):
                vect[r] = 0
    else:
        for r in range(rows):
            if not np.isnan(vect[r]):
                vect[r] = float(vect[r] - minimum)/(maximum - minimum)

def normalizeByZScore(vect):
    rows = vect.shape[0]
    data = np.array(map(lambda x: x, vect))
    data = [x for x in data if not np.isnan(x)]
    if len(data) == 0:
        return
    sd = np.std(data)
    mean = np.mean(data)
    if sd == 0:
        for r in range(rows):
            if not np.isnan(vect[r]):
                vect[r] = 0
    else:
        for r in range(rows):
            if not np.isnan(vect[r]):
                vect[r] = float(vect[r] - mean)/sd


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
    print "------------splitOffAttr-----------"
    print splitOffAttr(testMat, testDict, "B")
    print "----------- removeSparseAttributes -----------"
    print removeSparseAttributes(testMat, testDict)
    print "----------- smoothByReplacement(0)------------"
    print transformColumns(np.copy(testMat), smoothByReplacement(0))
    print "----------- smoothByAverage ------------------"
    print transformColumns(np.copy(testMat), smoothByAverage)
    print "----------- normalizeByMinMax----------------"
    print transformColumns(np.copy(testMat), normalizeByMinMax)
    print "----------- normalizeByZScore ---------------"
    print transformColumns(np.copy(testMat), normalizeByZScore)
