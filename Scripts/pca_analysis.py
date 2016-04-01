import sys
sys.path.append('../Util')

from database_reader import DatabaseReader
import matrix_cleaning as clean
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

    # Regression on
    """ TODO: make this more paramaterizable """
    tmpCoeffs, residual = LA.lstsq(pcaMat, vect)[:2]
    tmpCoeffs = tmpCoeffs.T

    # Transform back into original basis
    addedOn = (0 if yearRange is None else 1) \
            + (0 if constant is None else 1)
    coeffs = pca.inverse_transform(
            tmpCoeffs[:(len(tmpCoeffs) - addedOn)])
    for coeff in tmpCoeffs[(len(tmpCoeffs) - addedOn):]:
        coeffs.push()

    return coeffs, mat, dic

def doPCA(mat, components = 5):
    pca = PCA(n_components = components)
    mat = pca.fit_transform(mat)
    return mat, pca


if __name__ == '__main__':
    db = DatabaseReader()
    testData, testDic = db.fetchCountryData("United States")
    testData, testDic = clean.removeSparseAttributes(testData, testDic)
    clean.transformColumns(testData, clean.smoothByAverage)
    clean.transformColumns(testData, clean.normalizeByZScore)
    testData, testDic, vect = clean.splitOffAttr(testData,
            testDic, "Lending interest rate (%)")
    pcRegression(testData, testDic, vect)
