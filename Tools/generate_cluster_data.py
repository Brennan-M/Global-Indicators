'''for a single attribute and year, generate k clusters for all the countries'''

import sqlite3
from sklearn.cluster import KMeans

DB_PATH = '../Data/world-development-indicators/database.sqlite'

class Cluster(object):
	def __init__(self, k, year, attribute, path=DB_PATH):
		self.k = k
		self.year = year
		self.attribute = attribute
		self.kMeansClusters = None
		self.centers = []
		self.clusters = None

		self.values = []

		self.conn = sqlite3.connect(path, check_same_thread = False)
		self.conn.text_factory = str
		self.c = self.conn.cursor()

		self.countryCodes = {}
		self.countryInfo = {} # In format { CountryCode: {Year:Value, Year:Value, etc}, CountryCode: ... }
		self.organizedInfo = {} # In format { Year: {country:value, country:value, etc}, Year: ... }
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

	def getValues(self):
		yearInfo = self.organizedInfo[self.year]
		for key in yearInfo:
			self.values.append([self.year,yearInfo[key]])

	def kmeans(self):
		self.kMeansClusters = KMeans(n_clusters=self.k,init='k-means++')
		#self.kMeansClusters.fit(self.values)
		self.clusters = self.kMeansClusters.fit_predict(self.values)
		self.centers = self.kMeansClusters.cluster_centers_

if __name__ == "__main__":
  	cluster = Cluster(3, 2014, "NY.GDP.MKTP.CN")
  	print "country info USA"
  	#print cluster.countryInfo["USA"]
  	cluster.normalizeDataByYear()
  	cluster.getValues()
  	# print cluster.values
  	# print "year info 2014"
  	# print cluster.organizedInfo[2014]
  	# print ()
  	#print cluster.countryInfo["HPC"]
  	cluster.kmeans()
	print "year info 2014 CLUSTER"
  	print cluster.clusters
  	print "CENTERS"
  	print cluster.centers