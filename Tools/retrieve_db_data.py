import sqlite3

DB_PATH = '../Data/world-development-indicators/database.sqlite'


class RetrieveData(object):

	def __init__(self, path=DB_PATH):
		self.conn = sqlite3.connect(path, check_same_thread = False)
		self.conn.text_factory = str
		self.c = self.conn.cursor()

		self.data = {}

	def __del__(self):
		self.conn.close()

	def getIndicators(self):
		for row in self.c.execute("SELECT DISTINCT IndicatorCode, IndicatorName FROM Indicators"):
			self.data[row[0]] = row[1]

'''
if __name__ ==  "__main__":
	RD = RetrieveData()
	RD.getIndicators()
'''