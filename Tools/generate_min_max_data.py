import sqlite3
conn = sqlite3.connect('../Data/world-development-indicators/database.sqlite', check_same_thread=False)
conn.text_factory = str

c = conn.cursor()

class MinMax:

	def __init__(self, attributeInput):
		self.attributeAnalyzed = attributeInput
		self.countryCodes = {}
		self.countryInfo = {} # In format { CountryCode: {Year:Value, Year:Value, etc}, CountryCode: ... }
		self.organizedInfo = {} # In format { Year: {country:value, country:value, etc}, Year: ... }
		self.generateData()

	def generateData(self):
		for row in c.execute("SELECT CountryCode, TableName FROM Country"):
			self.countryCodes.update({row[1]:row[0]})

		minimum = float("inf")
		maximum = float("-inf")
		minYear = 3000
		maxYear = 0

		for country in self.countryCodes.keys():
			countryValues = {}
			for row in c.execute("SELECT Year, Value FROM Indicators WHERE IndicatorCode=? AND CountryName=?", (self.attributeAnalyzed, country)):
				countryValues.update({int(row[0]):int(row[1])})
				# Possibly this could be more efficient, but I am tired
				#if float(row[1]) < minimum:
				#	minimum = float(row[1])
				#if float(row[1]) > maximum:
				#	maximum = float(row[1])
				if int(row[0]) < minYear:
					minYear = int(row[0])
				if int(row[0]) > maxYear:
					maxYear = int(row[0]) 

			self.countryInfo.update({self.countryCodes[country]:countryValues})

		# This Code Normalizes the values
		# for obj in self.countryInfo.values():
		# 	for year, value in obj.items():
		# 		normalizedValue = (value - minimum) / (maximum - minimum)
		# 		obj[year] = normalizedValue

		for year in range(minYear, maxYear+1):
			newData = {}
			for ccode in self.countryInfo.keys():
				obj = self.countryInfo[ccode]
				if obj.has_key(year):
					newData[ccode] = obj[year]
				else:
					newData[ccode] = 0

			self.organizedInfo[year] = newData

		print self.organizedInfo


	def fuckYouMonaco(self):
		print self.countryInfo["MCO"]

# if __name__ == "__main__":
# 	minmax = MinMax("NY.GDP.PCAP.CD")
