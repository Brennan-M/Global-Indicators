from database_reader import DatabaseReader
import matrix_cleaning as clean
from matplotlib.pyplot import *

import numpy as np
import numpy.linalg as LA
from scipy.interpolate import *
from scipy import stats
# from sklearn import linear_model
# from sklearn.linear_model import LinearRegression
# from sklearn.linear_model import Ridge
#from sklearn.preprocessing import PolynomialFeatures

"""
Author: Michael Feller

This Util will be able to take in a country, attribute, and date range then return the 
coefficients for the line of best fit, as determined by a set of selectable
regression methods. 
"""

class baseRegress(object):

	def __init__(self, attribute, country):
		self.attribute = attribute
		self.country = country
		self.availYears = []
		self.attValues = []

	def build(self, dateRange):

		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
				self.country, (dateRange[0], dateRange[1]), asNumpyMatrix = False)

		#Read attribute values for each year in object attValue list
		for year in range(0, len(dataMatrix)):
			self.availYears.append(dateRange[0] + year)
			self.attValues.append(dataMatrix[year][attributeDict[self.attribute]])

	def lin_reg(self, degree, normalize):
		#Change attribute and year arrays to numpy arrays
		x = np.asarray(self.availYears)
		y = np.asarray(self.attValues)

		if (normalize == True):
			y = stats.zscore(y)
		
		pfit = np.polyfit(x,y,degree)

		"""Uncomment to plot regression line with points"""
		# plot(x,y,'o')
		# plot(x,np.polyval(pfit,x),'r-')
		# show()
		
		return pfit

	"""Implementation of ridge regression still needs work"""
	"""
	def ridge_reg():
		X = self.availYears[:, np.newaxis]
		Y = self.attValues[:, np.newaxis]

		clf = linear_model.Ridge(alpha = 1.0)
		clf.fit(X, Y)
		print clf.coef_
		return clf.coef_
	"""
	

if __name__ == "__main__":
	reg = baseRegress("NY.GDP.MKTP.CD", "United States")
	reg.build((1995, 2014))
	coefs = reg.lin_reg(1, True)
	#ridge_coefs = reg.ridge_reg
	print(coefs)

