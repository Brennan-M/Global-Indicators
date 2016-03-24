import sqlite3

DB_PATH = '../Data/world-development-indicators/database.sqlite'


class MinMax(object):

	def __init__(self, path=DB_PATH, attributeInput):
		self.conn = sqlite3.connect(path, check_same_thread = False)
		self.conn.text_factory = str
		self.c = self.conn.cursor()

		self.attributeAnalyzed = attributeInput
		self.countryCodes = {}
		self.countryInfo = {} # In format { CountryCode: {Year:Value, Year:Value, etc}, CountryCode: ... }
		self.organizedInfo = {} # In format { Year: {country:value, country:value, etc}, Year: ... }
		self.generateData()

	def __del__(self):
		self.conn.close()

	def generateData(self):

		# ccodesList = []
		# with open("ccodes.txt") as f:
		# 	for line in f:
		# 		ccodesList.append(line[:-1])
		invalidCcodes = ["ADO", "ARB", "CSS", "CEB", "CHI", "CUW", "ZAR", "EAS", "EAP",
		   "EMU", "ECS", "ECA", "EUU", "FCS", "HPC", "HIC", "NOC", "OEC", "IMY", "KSV",
		   "LCN", "LAC", "LDC", "LMY", "LIC", "LMC", "MEA", "MNA", "MIC", "NAC", "OED",
		   "OSS", "PSS", "ROM", "SXM", "SST", "SAS", "SSD", "SSF", "SSA", "TMP", "UMC",
		   "WBG", "WLD"]


		for row in self.c.execute("SELECT CountryCode, TableName FROM Country"):
			if row[0] in invalidCcodes:
				continue
			self.countryCodes.update({row[1]:row[0]})

		minimum = float("inf")
		maximum = float("-inf")
		minYear = float("inf")
		maxYear = float("-inf")

		for country, ccode in self.countryCodes.items():
			countryValues = {}
			for row in self.c.execute("SELECT Year, Value FROM Indicators WHERE IndicatorCode=? AND CountryName=?", (self.attributeAnalyzed, country)):
				countryValues.update({int(row[0]):int(row[1])})
				
				if float(row[1]) < minimum:
					minimum = float(row[1])
				if float(row[1]) > maximum:
					maximum = float(row[1])
					maxCountry = country
				if int(row[0]) < minYear:
					minYear = int(row[0])
				if int(row[0]) > maxYear:
					maxYear = int(row[0]) 

			self.countryInfo.update({self.countryCodes[country]:countryValues})

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


# if __name__ == "__main__":
  	# minmax = MinMax("NY.GDP.MKTP.CN")
  	# print minmax.countryInfo["USA"]
  	# print ()
  	# print minmax.countryInfo["HPC"]
