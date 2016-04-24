import sys
sys.path.append('../Util')
from database_reader import DatabaseReader
import matrix_cleaning as Clean

import sqlite3

DB_PATH = '../Data/world-development-indicators/database.sqlite'


class MinMax(object):

    def __init__(self, path=DB_PATH):
	    self.db = DatabaseReader(path)

    def generateData(self, attribute, normalization, smoothing):
	    print attribute
	    data, rowDic, colDic = self.db.fetchAttributeOverTimeData(attribute)
            data, rowDic = Clean.removeInvalidCountries(data, rowDic)
	    data, colDic = Clean.findValidTimeRange(data, colDic)

	    # Take the transpose
	    data = data.T
	    rowDic, colDic = colDic, rowDic


            # Do some smoothing
            if smoothing == "replacement":
                data = Clean.transformColumns(data, Clean.smoothByReplacement(0))
            elif smoothing == "average":
                data = Clean.transformColumns(data, Clean.smoothByAverage)
            elif smoothing == "interpolation":
                data = Clean.transformColumns(data, Clean.smoothByInterpolation)

            # Do some normalization
            if normalization == "global-min-max":
                data = Clean.normalizeByGlobalMinMax(data.T).T
            elif normalization == "min-max":
                data = Clean.transformColumns(data.T, Clean.normalizeByMinMax).T
            elif normalization == "z-score":
                data = Clean.transformColumns(data.T, Clean.normalizeByZScore).T

            Clean.normalizeByMinMax(data.T[:, 0])

	    return Clean.transformToDictionary(data, rowDic, colDic)

def test():
    mm = MinMax()
    mm.generateData("NY.GDP.MKTP.KD", "", "")
    
"""
if __name__ == '__main__':
    test()
"""