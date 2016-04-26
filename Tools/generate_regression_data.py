import sys
sys.path.append('../Util')
import math

from database_reader import DatabaseReader
import matrix_cleaning as clean
from matplotlib.pyplot import *
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge

import numpy as np
#import numpy.linalg as LA
from scipy.interpolate import *
from scipy import stats
from find_correlation_data import CorrelatedIndicators


class RegressionModel(object):
	
	def __init__(self, attribute, country):
		self.attribute = attribute
		self.country = country
		#self.attlist = attlist

	def actual(self):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
		self.country, (1960, 2014), useCountryCode=False, asNumpyMatrix=False)

		try:
			clean.transformColumns(dataMatrix, clean.smoothByAverage)
		except ValueError:
			clean.transformColumns(dataMatrix, clean.smoothByReplacement(0))

		# for year in dataMatrix:
		# 	print year

		valid = False
		for key,value in attributeDict.items():
			if(key == self.attribute):
				valid = True

		if (valid == False):
			return 0


		yt_ = [] #un-numpified training data for y
		for year in range(0, len(dataMatrix)):
			yt_.append(dataMatrix[year][attributeDict[self.attribute]])

		yt_ = np.asarray(yt_) #numpify target training data

		x_ = []
		for year in range(1960,2015):
			x_.append(year)

		actualdict = {}
		for num in range(0, len(x_)):
			actualdict[x_[num]] = yt_[num]

		for key, value in actualdict.items():
			if(math.isnan(value)):
				del(actualdict[key])

		return actualdict



	def polynomial(self, degree, attributes):

		"""Read in limited database for training"""
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
		self.country, (1960, 2000), useCountryCode=False, asNumpyMatrix=False)

		try:
			clean.transformColumns(dataMatrix, clean.smoothByAverage)
		except ValueError:
			clean.transformColumns(dataMatrix, clean.smoothByReplacement(0))

		valid = False
		for key,value in attributeDict.items():
			if(key == self.attribute):
				valid = True

		if (valid == False):
			return 0


		"""Initialize, fill, and convert target data for training"""
		yt_ = [] #un-numpified training data for y
		for year in range(0, len(dataMatrix)):
			yt_.append(dataMatrix[year][attributeDict[self.attribute]])

		yt_ = np.asarray(yt_) #numpify target training data

		"""Create list of weights by normalizing correlation values of attributes"""
		"""corrList = []
		weights = []

		ci = CorrelatedIndicators(self.attribute, self.country)
		correlations = ci.calculateCorrelations()

		for name in range(0, len(attributes)):
			#print 1
			for att in ci.correlationValues:
				if (attributes[name] == att[0]):
					#print att[1]
					temp = abs(att[1])
					corrList.append(temp)

		#Normalize correlation values and store as weights
		if(len(attributes) > 1):
			for corr in corrList:
				corr = (corr - min(corrList))/(2*(max(corrList)-min(corrList)))+0.5
				weights.append(corr.astype(float))
		else:
			weights = [1]

		#Zip attribute names and weights for ease of use
		attweights = zip(attributes, weights)"""		

		"""This section creates lists of regression line equations for use in predictions"""
		polylines = []
		eqList = []
		
		#Iterate through attributes and calculate regression lines for each against the target attribute
		for att in attributes:
			xt_ = [] #un-numpified training data for x
			for year in range(0, len(dataMatrix)):
				temp = dataMatrix[year][attributeDict[att]]
				xt_.append(temp)

			xt_ = np.asarray(xt_) #numpify training data for x

			pfit = np.polyfit(xt_,yt_,degree)
			poly = np.poly1d(pfit)
			eqList.append(poly)

			pfit = tuple(pfit)
			polylines.append(pfit)

		"""Read in data up to modelYear, for modeling and comparison"""
		db2 = DatabaseReader()
		dataMatrix2, colDictionary2, attributeDict2 = db.fetchCountryData(
		self.country, (1960, 2014), useCountryCode=False, asNumpyMatrix = False)

		"""Initialize new copy of target attribute data and populate for comparison""" 
		yp_ = yt_
		x_ = []

		for year in range(1960, 2015):
			x_.append(year)

		x_ = np.asarray(x_)

		tempval = 0
		tempsum = 0
		totsum = 0

		#print sum(weights)

		for year in range(41, 55):
			totsum = 0
			numsum = 0
			for num in range(0, len(attributes)):
				xtemp = dataMatrix2[year][attributeDict2[attributes[num]]]
				regtemp = eqList[num]
				totsum = totsum + (regtemp(xtemp))
				numsum += 1
			yp_ = np.append(yp_, totsum/(len(attributes)))

		polydict = {}
		for num in range(0, len(x_)):
			polydict[x_[num]] = yp_[num]

		for key, value in polydict.items():
			if(math.isnan(value)):
				del(polydict[key])

		return polydict

	def ridge(self, attributes):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
		self.country, (1960, 2000), useCountryCode=False, asNumpyMatrix=False)

		try:
			clean.transformColumns(dataMatrix, clean.smoothByAverage)
		except ValueError:
			clean.transformColumns(dataMatrix, clean.smoothByReplacement(0))

		valid = False
		for key,value in attributeDict.items():
			if(key == self.attribute):
				valid = True

		if (valid == False):
			return 0

		db2 = DatabaseReader()
		dataMatrix2, colDictionary2, attributeDict2 = db.fetchCountryData(
		self.country, (2001, 2014), useCountryCode=False, asNumpyMatrix = False)

		try:
			clean.transformColumns(dataMatrix2, clean.smoothByAverage)
		except ValueError:
			clean.transformColumns(dataMatrix2, clean.smoothByReplacement(0))


		"""Initialize, fill, and convert target data for training"""
		yt_ = [] #un-numpified training data for y
		for year in range(0, len(dataMatrix)):
			yt_.append(dataMatrix[year][attributeDict[self.attribute]])

		yt_ = np.asarray(yt_) #numpify target training data

		yp_ = yt_

		for year in range(0, len(dataMatrix2)):
			tempsum = 0
			for att in attributes:
				xt = [] #un-numpified training data for x
				for year2 in range(0, len(dataMatrix)):
					temp = dataMatrix[year2][attributeDict[att]]
					xt.append(temp)

				xt_ = np.asarray(xt) #numpify training data for x

				xt_ = np.reshape(xt_,(41,1))

				clf = linear_model.Ridge()
				clf.fit(xt_, yt_)
				tempred = clf.predict(dataMatrix2[year][attributeDict2[att]])
				tempsum = tempsum+tempred
			tempval = tempsum/len(attributes)
			yp_ = np.append(yp_,tempval)

		x_ = []
		for year in range(1960, 2015):
			x_.append(year)
		x_ = np.asarray(x_)

		ridgedict = {}
		for num in range(0, len(x_)):
			ridgedict[x_[num]] = yp_[num]

		for key, value in ridgedict.items():
			if(math.isnan(value)):
				del(ridgedict[key])

		return ridgedict


	def log(self, attributes):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
		self.country, (1960, 2000), useCountryCode=False, asNumpyMatrix=False)

		try:
			clean.transformColumns(dataMatrix, clean.smoothByAverage)
		except ValueError:
			clean.transformColumns(dataMatrix, clean.smoothByReplacement(0))

		valid = False
		for key,value in attributeDict.items():
			if(key == self.attribute):
				valid = True

		if (valid == False):
			return 0

		db2 = DatabaseReader()
		dataMatrix2, colDictionary2, attributeDict2 = db.fetchCountryData(
		self.country, (2001, 2014), useCountryCode=False, asNumpyMatrix = False)


		"""Initialize, fill, and convert target data for training"""
		yt_ = [] #un-numpified training data for y
		for year in range(0, len(dataMatrix)):
			yt_.append(dataMatrix[year][attributeDict[self.attribute]])

		yt_ = np.asarray(yt_) #numpify target training data

		yp_ = yt_

		for year in range(0, len(dataMatrix2)):
			tempsum = 0
			for att in attributes:
				xt = [] #un-numpified training data for x
				for year2 in range(0, len(dataMatrix)):
					temp = dataMatrix[year2][attributeDict[att]]
					xt.append(temp)

				xt_ = np.asarray(xt) #numpify training data for x

				xt_ = np.reshape(xt_,(41,1))

				llf = linear_model.LogisticRegression(penalty = 'l2')
				llf.fit(xt_, yt_)
				tempred = llf.predict(dataMatrix2[year][attributeDict2[att]])
				tempsum = tempsum+tempred
			tempval = tempsum/len(attributes)
			yp_ = np.append(yp_,tempval)

		x_ = []
		for year in range(1960, 2015):
			x_.append(year)
		x_ = np.asarray(x_)

		logdict = {}
		for num in range(0, len(x_)):
			logdict[x_[num]] = yp_[num]

		return logdict

	def packRegs(self, predictors):
		act = self.actual()
		poly2 = self.polynomial(2,predictors)
		poly3 = self.polynomial(3,predictors)
		rid = self.ridge(predictors)

		return act,poly2,poly3,rid



if __name__ == "__main__":
	model = RegressionModel("NY.GDP.MKTP.KD", "United States")
	pack = model.packRegs(['EG.ELC.PETR.ZS','EN.URB.MCTY.TL.ZS'])
	print pack
	# actual = model.actual()
	# poly1 = model.polynomial(1, ['EG.ELC.PETR.ZS','EN.URB.MCTY.TL.ZS'])
	# poly2 = model.polynomial(2, ['EG.ELC.PETR.ZS','EN.URB.MCTY.TL.ZS']) #, 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS']) #, 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	# # poly2 = model.polynomial(2, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	# # poly3 = model.polynomial(5, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	# ridge = model.ridge(['EG.ELC.PETR.ZS','EN.URB.MCTY.TL.ZS'])
	# #log = model.log(['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	
	# #print log
	# if(poly1 != 0):
	# 	px1 = []
	# 	py1 = []
	# 	for key, value in poly1.items():
	# 		px1.append(key)
	# 		py1.append(value)
	# 	plot(px1,py1,'r-')
	# else:
	# 	print "Not a valid attribute"
	# if(poly2 != 0):
	# 	px2 = []
	# 	py2 = []
	# 	for key, value in poly2.items():
	# 		px2.append(key)
	# 		py2.append(value)
	# 	plot(px2,py2,'b-')
	# else:
	# 	print "Not a valid attribute"
	# px3 = []
	# py3 = []
	# for key, value in poly3.items():
	# 	px3.append(key)
	# 	py3.append(value)
	# plot(px3,py3,'y-')
	# rx = []
	# ry = []
	# for key, value in ridge.items():
	# 	rx.append(key)
	# 	ry.append(value)
	# plot(rx,ry,'bo')
	# if (actual != 0):
	# 	ax = []
	# 	ay = []
	# 	for key, value in actual.items():
	# 		ax.append(key)
	# 		ay.append(value)
	# 	plot(ax,ay,'g-')
	# 	show()
	# else:
	# 	print "Invalid target Attribute"