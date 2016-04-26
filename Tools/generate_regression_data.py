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

"""Author: Michael Feller"""


class RegressionModel(object):
	
	def __init__(self, attribute, country):
		self.attribute = attribute
		self.country = country
		#self.attlist = attlist

	def cleanAttributes(self, attributes):
		db = DatabaseReader()
		dataMatrix, colDictionary, attributeDict = db.fetchCountryData(
		self.country, (1960, 2014), useCountryCode=False, asNumpyMatrix=False)

		ret_atts = []
		for key,value in attributeDict.items():
			for att in attributes:
				if(key == att):
					ret_atts.append(att)

		return ret_atts

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
			for num in range(0, len(attributes)):
				xtemp = dataMatrix2[year][attributeDict2[attributes[num]]]
				regtemp = eqList[num]
				totsum = totsum + (regtemp(xtemp))
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

				clf = linear_model.Ridge(alpha = 0)
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

		predicted_values = []

		for att in attributes:
			xt_ = []
			for year in range(0, len(dataMatrix)):
				temp = dataMatrix[year][attributeDict[att]]
				xt_.append(temp)

			xt_ = np.asarray(xt_)

			xt_ = np.reshape(xt_,(41,1))

			llf = linear_model.LogisticRegression(penalty = 'l2')
			llf.fit_transform(xt_,yt_.astype(int))

			temparray = []

			for year2 in range(0,len(dataMatrix2)):
				tempval = llf.predict(dataMatrix2[year2][attributeDict2[att]])
				temparray.append(tempval)

			predicted_values.append(temparray)

		for num in range(0,len(predicted_values[0])):
			sum1 = 0
			for num2 in range(0,len(predicted_values)):
				sum1 = sum1 + predicted_values[num2][num]
			temp = sum1/len(predicted_values)
			yp_=np.append(yp_,temp)

		x_ = []
		for year in range(1960, 2015):
			x_.append(year)
		x_ = np.asarray(x_)

		logdict = {}
		for num in range(0, len(x_)):
			logdict[x_[num]] = yp_[num]

		for key, value in logdict.items():
			if(math.isnan(value)):
				del(logdict[key])

		return logdict

	def packRegs(self, predictors):
		cleanatts = self.cleanAttributes(predictors)
		act = self.actual()
		poly2 = self.polynomial(2,cleanatts)
		rid = self.ridge(cleanatts)

		return cleanatts,act,poly2,rid



if __name__ == "__main__":
	model = RegressionModel("NY.GDP.MKTP.KD", "United States")
	pack = model.packRegs(['EG.ELC.PETR.ZS','EN.URB.MCTY.TL.ZS'])
	#print pack
	actual = model.actual()
	poly1 = model.polynomial(1, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	poly2 = model.polynomial(2, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS']) #, 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS']) #, 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	# # poly2 = model.polynomial(2, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	# # poly3 = model.polynomial(5, ['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	ridge = model.ridge(['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	#log = model.log(['EN.URB.MCTY.TL.ZS', 'NY.GDP.MKTP.CD', 'EN.URB.MCTY', 'SP.URB.TOTL.IN.ZS', 'SP.RUR.TOTL.ZS'])
	#print log
	# #print log
	if(poly1 != 0):
		px1 = []
		py1 = []
		for key, value in poly1.items():
			px1.append(key)
			py1.append(value)
		plot(px1,py1,'r-')
	else:
		print "Not a valid attribute"
	if(poly2 != 0):
		px2 = []
		py2 = []
		for key, value in poly2.items():
			px2.append(key)
			py2.append(value)
		plot(px2,py2,'b-')
	else:
		print "Not a valid attribute"
	# px3 = []
	# py3 = []
	# for key, value in poly3.items():
	# 	px3.append(key)
	# 	py3.append(value)
	# plot(px3,py3,'y-')
	lx = []
	ly = []
	for key, value in ridge.items():
		lx.append(key)
		ly.append(value)
	plot(lx,ly,'bo')
	if (actual != 0):
		ax = []
		ay = []
		for key, value in actual.items():
			ax.append(key)
			ay.append(value)
		plot(ax,ay,'g-')
		show()
	else:
		print "Invalid target Attribute"