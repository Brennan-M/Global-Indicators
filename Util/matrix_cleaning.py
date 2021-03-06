import numpy as np
from scipy.interpolate import interp1d

"""
Author: Ian Char

Util functions for cleaning matrices.
"""


YEAR_DIC_VALUE = "Year"
CONSTANT_DIC_VALUE = "Constant"
INVLID_COUNTRY_COUDES = ["ADO", "ARB", "CSS", "CEB", "CHI", "CUW", "ZAR", "EAS", "EAP",
		   "EMU", "ECS", "ECA", "EUU", "FCS", "HPC", "HIC", "NOC", "OEC", "IMY", "KSV",
		   "LCN", "LAC", "LDC", "LMY", "LIC", "LMC", "MEA", "MNA", "MIC", "NAC", "OED",
		   "OSS", "PSS", "ROM", "SXM", "SST", "SAS", "SSD", "SSF", "SSA", "TMP", "UMC",
		   "WBG", "WLD"]

"""
Here we assume that the countries are on the rows of the Matrix. The Matrix
and row dictionary will remain unchanged. THe new values will be returned.
"""
def removeInvalidCountries(mat, rowDic):
    rows, cols = mat.shape
    toRemove = []

    for key, value in rowDic.items():
        if value in INVLID_COUNTRY_COUDES:
            toRemove.append(key)

    newMat = np.asmatrix(np.empty((rows - len(toRemove), cols)))
    newDic = {}

    currRow = 0
    for r in range(rows):
        if r not in toRemove:
            newMat[currRow, :] = mat[r, :]
            newDic[currRow] = rowDic[r]
            currRow += 1

    return newMat, newDic


"""
Takes a matrix and gives back a nested dictionary where the outer layer of
the dictionary is indexed by the rows and the inner dictionaries are indexed
by the columns
"""
def transformToDictionary(mat, rowDic, colDic):
    numRows, numCols = mat.shape
    toReturn = {}

    for r in range(numRows):
        innerDic = {}
        for c in range(numCols):
            innerDic[colDic[c]] = mat[r, c]
        toReturn[rowDic[r]] = innerDic

    return toReturn

"""
Add a column to the end of the matrix the value to be added can be a range
of numbers represented as a tuple (inclusive), or a single number. This will
make a shallow copy of the matrix but alter the dictionary given. Returns new
matrix and altered dictionary.
"""
def addColumn(mat, colDic, colName, value):
    rows, cols = mat.shape
    toFill = []
    if isinstance(value, tuple):
        if value[1] - value[0] + 1 != rows:
            raise RuntimeError("Value given does not span the rows of matrix.")
        toFill = range(value[0], value[1] + 1)
    else:
        toFill = [value for _ in range(rows)]

    newMat = np.asmatrix(np.empty((rows, cols + 1)))
    newMat[:, :cols] = mat
    for elemNum, elem in enumerate(toFill):
        newMat[elemNum, cols] = elem

    colDic[cols] = colName

    return newMat, colDic


"""
Splits the given name of the attribute off from the matrix and returns it as a
vector. Returns a new matrix (old one not altered), new dict (old one not
altered), and the vector of the attribute.
"""
def splitOffAttr(mat, colDic, attribute):
    rows, cols = mat.shape

    # Find index in matrix corresponding to attribute
    attrIndex = -1
    for key, val in colDic.items():
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
    for key, val in colDic.items():
        if key != attrIndex:
            newDic[key if key < attrIndex else key - 1] = val

    return newMat, newDic, attrVect


"""
Looks through the matrix and will remove any column that has more missing
values than the tolerance provided where the tolerance is the percent of
overall values.

Returns an updated matrix and an updated dictionary
"""
def removeSparseAttributes(mat, colDic, tolerance = 0.8):
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
        newDic[currCol] = colDic[c]
        currCol += 1

    return newMat, newDic

"""
Cuts off consecutive columns that have a certain amount of non-nans. We assume
here that the years are on the columns.
"""
def findValidTimeRange(mat, colDic, nanUpperThreshold = 1.0):
    rows, cols = mat.shape
    start = 0
    end = cols - 1
    accFunc = accFunc = lambda prev, curr: 1 + prev if np.isnan(curr) else prev

    # Find a good start
    nanAmount = 1.0
    while nanAmount >= nanUpperThreshold:
        nanAmount = reduce(accFunc, mat[:, start], 0)/float(rows)
        if nanAmount >= nanUpperThreshold:
            start += 1

    # Find a good end
    nanAmount = 1.0
    while nanAmount > nanUpperThreshold:
        nanAmount = reduce(accFunc, mat[:, end], 0)/float(rows)
        if nanAmount >= nanUpperThreshold:
            end -= 1

    if start > end:
        print "No valid time range could be found for the data!", start, end
        return np.matrix([[np.NAN]]), {}

    # fit mat and dict to this range
    validRange = range(start, end + 1)
    for key in colDic.keys():
        if key not in validRange:
            del colDic[key]

    # Readjust dic values
	newDic = {}
    for c in range(cols):
        if c <= end - start:
            newDic[c] = colDic[c + start]

    return mat[:, start:end + 1], newDic
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

def smoothByInterpolation(vect):
    toTrainX = []
    toTrainY = []
    toPredict = []
    rows = vect.shape[0]

    for r in range(rows):
        if np.isnan(vect[r]):
            toPredict.append(r)
        else:
            toTrainX.append(r)
            toTrainY.append(vect[r][0,0])

    if len(toTrainX) <= 3:
        print "Not enough data to interpolate"
        smoothByAverage(vect)
        return

    f = interp1d(toTrainX, toTrainY, kind='cubic')

    for index in toPredict:
        if index < toTrainX[0]:
            vect[index] = toTrainY[0]
        elif index > toTrainX[-1]:
            vect[index] = toTrainY[-1]
        else:
            vect[index] = f(index)

""" Normalizing functions """
def normalizeByMinMax(vect):
    rows = vect.shape[0]
    minimum = float('inf')
    maximum = float('-inf')
    for r in range(rows):
        if float(vect[r]) < minimum:
            minimum = float(vect[r])
        if float(vect[r]) > maximum:
            maximum = float(vect[r])
    if maximum - minimum < 10 ** -8:
        for r in range(rows):
            if not np.isnan(vect[r]):
                vect[r] = 0
    else:
        countAdjust = 0
        for r in range(rows):
            if not np.isnan(vect[r]):
                toReplace = float(float(vect[r]) - minimum)/(maximum - minimum)
                if toReplace > 1 or toReplace < 0:
                    print "wtf...", int(vect[r]), minimum, maximum
                else:
                    vect[r] = toReplace
                countAdjust += 1
        print countAdjust, rows

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

# Unlike the other normalizing functions this is not to be used in conjuction
# with transformColumns
def normalizeByGlobalMinMax(mat):
    rows, cols = mat.shape
    minimum = float('inf')
    maximum = float('-inf')

    # Find the minimum and maximum
    for r in range(rows):
        for c in range(cols):
            if mat[r, c] < minimum:
                minimum = mat[r, c]
            if mat[r, c] > maximum:
                maximum = mat[r, c]

    # Normalize all elements
    for r in range(rows):
        for c in range(cols):
            toDivide = maximum if maximum == minimum else maximum - minimum
            mat[r, c] = (mat[r, c] - minimum)/float(toDivide)
    return mat


def testBasics():
    testMat = np.matrix([[np.NAN, 2, 3, 4],
                        [np.NAN, 2, 8, 3],
                        [np.NAN, np.NAN, 5, 5],
                        [np.NAN, np.NAN, 2, 3],
                        [np.NAN, 2, np.NAN, 5]])
    testDict = {0:"A", 1:"B", 2:"C", 3:"D"}
    print "----------- Test Matrix -----------"
    print testMat
    print testDict
    print "-------------findValidTimeRange--------------"
    print findValidTimeRange(np.copy(testMat), dict(testDict))
    print "------------addColumn--------------"
    print addColumn(testMat, dict(testDict), YEAR_DIC_VALUE, (17, 21))
    print addColumn(testMat, dict(testDict), CONSTANT_DIC_VALUE, 8)
    print "------------splitOffAttr-----------"
    print splitOffAttr(testMat, testDict, "B")
    print "----------- removeSparseAttributes -----------"
    print removeSparseAttributes(testMat, testDict)
    print "----------- smoothByReplacement(0)------------"
    print transformColumns(np.copy(testMat), smoothByReplacement(0))
    print "----------- smoothByAverage ------------------"
    print transformColumns(np.copy(testMat), smoothByAverage)
    print "----------- smoothByInterpolation ------------------"
    print transformColumns(np.copy(testMat), smoothByInterpolation)
    print "----------- normalizeByMinMax----------------"
    print transformColumns(np.copy(testMat), normalizeByMinMax)
    print "----------- normalizeByZScore ---------------"
    print transformColumns(np.copy(testMat), normalizeByZScore)
    print "----------- normalizeByGlobalMinMax ---------------"
    print normalizeByGlobalMinMax(np.copy(testMat))

def testTransformToDictionary():
    testMat = np.matrix([[np.NAN, 2, 3, 4],
                        [np.NAN, 2, 8, 3],
                        [np.NAN, np.NAN, 5, 5],
                        [np.NAN, np.NAN, 2, 3],
                        [np.NAN, 2, np.NAN, 5]])
    rowDic = {0:"V", 1:"W", 2:"X", 3:"Y", 4:"Z"}
    colDic = {0:"A", 1:"B", 2:"C", 3:"D"}
    print transformToDictionary(testMat, rowDic, colDic)

if __name__ == '__main__':
    testBasics()
    testTransformToDictionary()
