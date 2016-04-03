import numpy as np
import math
from scipy.stats.stats import pearsonr
import sys

sys.path.append('../Util/')
from database_reader import DatabaseReader

class CorrelatedIndicators(object):

	def __init__(self, attribute, country):
		self.attribute = attribute
		self.country = country

	def calculateCorrelations(self):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(self.country, (2010, 2014))

		correlations = {}
		for year in dataMatrix:
			#print year[attributeDict[self.attribute]]
			pass

		for year in dataMatrix:
			
			for col in range(0, len(year+1)):
				print year[col], year[attributeDict[self.attribute]]

				correlations[]
				#print col
		

		# So, we will take a single column of data over a span of years (our attribute), and compute
		# the correlation coefficient, 

	def findMostCorrelatedIndicators(self):
		pass


if __name__ == "__main__":
	ci = CorrelatedIndicators("NY.GDP.MKTP.CD", "United States")
	ci.calculateCorrelations()