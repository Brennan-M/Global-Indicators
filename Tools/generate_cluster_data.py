'''for a single attribute and year, generate k clusters for all the countries'''

import sqlite3
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

DB_PATH = '../Data/world-development-indicators/database.sqlite'

class Cluster(object):
	def __init__(self, k, year, attribute, path=DB_PATH):
		self.k = k # for k-means, ths number of clusters (not used in DBSCAN)
		self.year = year
		self.attribute = attribute
		self.kMeansClusters = None
		self.DBSCANClusters = None
		self.centers = [] 
		self.clusters = None #index of the cluster that data point belongs to

		self.values = [] # 2D array of the year and corresponding data point (all the years will be the same)
		self.countries = [] #list of country codes in same order of self.values (for putting together dictionary at the end)

		self.conn = sqlite3.connect(path, check_same_thread = False)
		self.conn.text_factory = str
		self.c = self.conn.cursor()

		self.countryCodes = {}
		self.countryInfo = {} # In format { CountryCode: {Year:Value, Year:Value, etc}, CountryCode: ... }
		self.organizedInfo = {} # In format { Year: {country:value, country:value, etc}, Year: ... }
		self.clusterInfo = {} # In format { CountryCode: cluster index, CountryCode: cluster index ... }
		self.generateData()

	# credit for del, generateData, normalizeData, and normalizeDataByYear
	# goes out to the homie Brennan
	def __del__(self):
		self.conn.close()

	def generateData(self):

		# ccodesList = []
		# with open("ccodes.txt") as f:
		# 	for line in f:
		# 		ccodesList.append(line[:-1])

		#codes of countries with incomplete data or that do not exist anymore
		invalidCcodes = ["ADO", "ARB", "CSS", "CEB", "CHI", "CUW", "ZAR", "EAS", "EAP",
		   "EMU", "ECS", "ECA", "EUU", "FCS", "HPC", "HIC", "NOC", "OEC", "IMY", "KSV",
		   "LCN", "LAC", "LDC", "LMY", "LIC", "LMC", "MEA", "MNA", "MIC", "NAC", "OED",
		   "OSS", "PSS", "ROM", "SXM", "SST", "SAS", "SSD", "SSF", "SSA", "TMP", "UMC",
		   "WBG", "WLD"]


		for row in self.c.execute("SELECT CountryCode, TableName FROM Country"):
			if row[0] in invalidCcodes:
				continue
			self.countryCodes.update({row[1]:row[0]})


		for country, ccode in self.countryCodes.items():
			countryValues = {}
			for row in self.c.execute("SELECT Year, Value FROM Indicators WHERE IndicatorCode=? AND CountryName=?", (self.attribute, country)):
				countryValues.update({int(row[0]):float(row[1])})

			self.countryInfo.update({self.countryCodes[country]:countryValues})


	def normalizeData(self):

		minimum = float("inf")
		maximum = float("-inf")
		minYear = float("inf")
		maxYear = float("-inf")

		for obj in self.countryInfo.values():
			for year, value in obj.items():
				if value < minimum:
					minimum = value
				if value > maximum:
					maximum = value
				if year < minYear:
					minYear = year
				if year > maxYear:
					maxYear = year 

		# This Code Normalizes the values
		for obj in self.countryInfo.values():
			for year, value in obj.items():
				normalizedValue = (value - minimum) / (maximum - minimum)
				obj[year] = normalizedValue

		for year in range(minYear, maxYear+1):
			newData = {}
			for ccode in self.countryInfo.keys():
				obj = self.countryInfo[ccode]
				if obj.has_key(year):
					newData[ccode] = obj[year]
				else:
					newData[ccode] = 0

			self.organizedInfo[year] = newData
		self.getValues()

	def normalizeDataByYear(self):

		minYear = float("inf")
		maxYear = float("-inf")
		
		for obj in self.countryInfo.values(): 
			for year in obj.keys():
				if year < minYear:
					minYear = year
				if year > maxYear:
					maxYear = year
		
		for year in range(minYear, maxYear+1):
			newData = {}
			for ccode in self.countryInfo.keys():
				obj = self.countryInfo[ccode]
				if obj.has_key(year):
					newData[ccode] = obj[year]
				else:
					newData[ccode] = 0

			self.organizedInfo[year] = newData


		# This Code Normalizes the values
		for year, obj in self.organizedInfo.items():

			localMin = float("inf")
			localMax = float("-inf")

			for value in obj.values():
				if value < localMin:
					localMin = value
				if value > localMax:
					localMax = value

			for country, value in obj.items():
				normalizedValue = (value - localMin) / (localMax - localMin)
				obj[country] = normalizedValue
		self.getValues()

	def getValues(self):
		yearInfo = self.organizedInfo[self.year]
		for key in yearInfo:
			self.values.append([self.year,yearInfo[key]])
			self.countries.append(key)

	def kmeans(self):
		# K-Means Clustering
		self.kMeansClusters = KMeans(n_clusters=self.k,init='k-means++')
		self.clusters = self.kMeansClusters.fit_predict(self.values)
		self.centers = self.kMeansClusters.cluster_centers_
		self.dict()

	def dbscan(self):
		# DBSCAN Clustering - currently does not work, giving it the wrong form of data
		self.DBSCANClusters = DBSCAN()
		self.clusters = self.DBSCANClusters.fit_predict(self.values)
		#self.centers = self.DBSCANClusters.core_sample_indices_
		self.dict()

	def dict(self):
		# putting the results into a  (for JSON output
		for i in range(0,len(self.countries)):
			country = self.countries[i]
			cnum = self.clusters[i]
			self.clusterInfo[country] = cnum


if __name__ == "__main__":
  	cluster = Cluster(10, 2014, "AG.LND.TOTL.K2") #NY.GDP.MKTP.KD.ZG - GDP growth rate, NY.GDP.MKTP.CD - GDP
  		#SG.VAW.ARGU.ZS - % women who think their husband is justified in beating her when she argues with him
  		#AG.LND.TOTL.K2  - land area in sq. km
  	cluster.normalizeDataByYear()
  	#cluster.normalizeData()
  	cluster.kmeans()
  	#cluster.dbscan()
  	# print cluster.countries
  	# print cluster.values
  	# print cluster.clusters
  	# print cluster.centers
  	print cluster.clusterInfo