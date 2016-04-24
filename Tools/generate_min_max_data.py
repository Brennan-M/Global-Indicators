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
		data, colDic = Clean.findValidTimeRange(data, colDic)
		data = Clean.transformColumns(data, Clean.normalizeByMinMax)
		return Clean.transformToDictionary(data.T, colDic, rowDic)
