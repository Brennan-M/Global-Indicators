import numpy as np
import math
from scipy.stats.stats import pearsonr
import sys

sys.path.append('../Util/')
from database_reader import DatabaseReader
import matrix_cleaning as clean

class CorrelatedIndicators(object):

	def __init__(self, attribute, country):
		self.attribute = attribute
		self.country = country
		self.correlationValues = {}

	def calculateCorrelations(self):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
				self.country, (2000, 2014), useCountryCode=False, asNumpyMatrix=False)

		#dataMatrix, colDictionary = clean.removeSparseAttributes(dataMatrix, colDictionary, 0.9)

		#Row is Year
		#Col is Attribute

		#dataMatrix = dataMatrix.tolist()

		#print dataMatrix

		attributeDictReverse = {}
		for key, value in attributeDict.items():
			attributeDictReverse[value] = key


		correlations = {}

		# My correlation dictionary should be in the form of {attribute: []}

		for key in attributeDict.keys():
			correlations[key] = []


		for year in range(0, len(dataMatrix)):
			for attr in range(0, len(dataMatrix[year])):
				correlations[attributeDictReverse[attr]].append(dataMatrix[year][attr])

		# I need to handle Nans.

		for attr, array in correlations.items():
			correlations[attr] = pearsonr(array, correlations[self.attribute])[0]

		values = list(correlations.values())
		keys = list(correlations.keys())


		for key, value in correlations.items():
			if math.isnan(value):
				del correlations[key]

		self.correlationValues = []
		for key, value in correlations.items():
			self.correlationValues.append((key, value))

		self.correlationValues = sorted(self.correlationValues, key=lambda x: x[1])

	def findMostCorrelatedIndicators(self, correlations, k):

		for key, value in correlations.items():
			if math.isnan(value):
				del correlations[key]

		values = list(correlations.values())
		keys = list(correlations.keys())

		newValues = map(lambda v : math.fabs(v), values)

		mostCorrelated = []

		for i in range(0, k):
			index = newValues.index(max(newValues))
			mostCorrelated.append({keys[index]:newValues[index]})
			del newValues[index]
			del keys[index]

		print mostCorrelated
		return mostCorrelated


if __name__ == "__main__":
	ci = CorrelatedIndicators("NY.GDP.MKTP.KD.ZG", "United States")
	ci.calculateCorrelations()
	print ci.correlationValues


