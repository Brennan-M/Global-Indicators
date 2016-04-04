import sys
sys.path.append('../Util')

from database_reader import DatabaseReader
import matrix_cleaning as clean
import plot
import numpy as np
import numpy.linalg as LA
from sklearn.decomposition import PCA


def pcRegression(mat, dic, vect, components = 5,
        yearRange = None, constant = None):
    # Train pca
    pcaMat, pca = doPCA(mat)
    pcaDic = {}
    for c in range(components):
        pcaDic[c] = "Component " + str(c)

    # Add to the any extra things to the matrix
    if yearRange is not None:
        pcaMat, pcaDic = clean.addColumn(pcaMat, pcaDic,
                clean.YEAR_DIC_VALUE, yearRange)
        mat, dic = clean.addColumn(mat, dic,
                clean.YEAR_DIC_VALUE, yearRange)
    if constant is not None:
        pcaMat, pcaDic = clean.addColumn(pcaMat, pcaDic,
                clean.CONSTANT_DIC_VALUE, constant)
        mat, dic = clean.addColumn(mat, dic,
                clean.CONSTANT_DIC_VALUE, constant)

    # Regression
    """ TODO: make this more paramaterizable """
    tmpCoeffs, residual = LA.lstsq(pcaMat, vect)[:2]
    tmpCoeffs = np.asmatrix(tmpCoeffs).T

    # Transform back into original basis
    addedOn = (0 if yearRange is None else 1) \
            + (0 if constant is None else 1)
    numTmpCoeffs = tmpCoeffs.shape[1]
    tmp = pca.inverse_transform(
            tmpCoeffs[:, :(numTmpCoeffs - addedOn)])
    coeffs = np.asmatrix(np.empty((1, tmp.shape[1] + addedOn)))
    coeffs[0, :tmp.shape[1]] = tmp[:, :tmp.shape[1]]
    for i in range(numTmpCoeffs - addedOn, numTmpCoeffs):
        coeffs[0, i] = tmpCoeffs[0, i]

    #TEST
    prediction = mat * np.asmatrix(coeffs).T
    plot.plotCountry(range(45), "Time (Years)", [(vect, "GDP"), (prediction, "Prediction")], "pcatest", decorations=['k', 'r'])


    return coeffs, mat, dic

def doPCA(mat, components = 5):
    pca = PCA(n_components = components)
    mat = pca.fit_transform(mat)
    return mat, pca

def getTopContributors(vals, dic, contributors = 10):
    vals = sorted(enumerate(vals), cmp = lambda x, y: cmp(abs(x[1]), abs(y[1])))
    place = 1
    for index, value in vals[:(-1 * contributors - 1):-1]:
        print place, dic[index], value
        place += 1


def testPCRegression():
    db = DatabaseReader()
    testData, testDic = db.fetchCountryData("United States")[:2]
    testData, testDic = clean.removeSparseAttributes(testData, testDic)
    clean.transformColumns(testData, clean.smoothByAverage)
    clean.transformColumns(testData, clean.normalizeByZScore)
    testData, testDic, vect = clean.splitOffAttr(testData,
            testDic, "GDP (constant LCU)")
    coeffs, testData, testDic = pcRegression(testData[:45,:], testDic, vect[:45,:], constant = 1)
    prediction = testData[:45, :] * np.asmatrix(coeffs).T
    plot.plotCountry(range(45), "Time (Years)", [(vect[:45,:], "GDP"),
            (prediction, "GDP Predicted")], "GDP vs Time", decorations=['k', 'r'])

def testPCA():
    db = DatabaseReader()
    testData, testDic = db.fetchCountryData("United States")[:2]
    testData = testData[:-1, :]
    testData, testDic = clean.removeSparseAttributes(testData, testDic)
    clean.transformColumns(testData, clean.smoothByAverage)
    clean.transformColumns(testData, clean.normalizeByZScore)
    testData, testDic, vect = clean.splitOffAttr(testData,
            testDic, "GDP (constant LCU)")

    pcaData, pcaObj = doPCA(testData[:45])
    print "_____________ explained variance ratio_______________"
    print pcaObj.explained_variance_ratio_

    pcaData, testDic = clean.addColumn(pcaData, testDic,
            clean.CONSTANT_DIC_VALUE, 1)
    coeffs, residual = LA.lstsq(pcaData, vect[:45])[:2]
    print "_______________ residual _______________"
    print residual
    coeffs = np.asmatrix(coeffs)

    # Find top 10
    print '_______________Top 10 of 1st Component________________'
    l = []
    e1 = np.matrix([[1, 0, 0, 0, 0]])
    for i in np.nditer(pcaObj.inverse_transform(e1)):
        l.append(i)
    getTopContributors(l, testDic)

    prediction = pcaData * coeffs
    plot.plotCountry(range(1960, 2005), "Year", [(vect[:45,:], "True GDP"),
            (prediction, "Predicted GDP")], "Normalized GDP vs Year", decorations=['k', 'r--'])

    predictData = pcaObj.transform(testData[45:])
    predictData, testDic = clean.addColumn(predictData, testDic,
            clean.CONSTANT_DIC_VALUE, 1)
    prediction = predictData * coeffs

    plot.plotCountry(range(2005, 2014), "Year", [(vect[45:,:], "True GDP"),
            (prediction, "Predicted GDP")], "Normalized GDP vs Year", decorations=['k', 'r--'])

if __name__ == '__main__':
    testPCA()
