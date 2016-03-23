import sqlite3
import numpy as np
"""
Author: Ian Char

Use this class to read information from the database.

When the object is constructed a connection will be opened to the database.
Make sure that when you are finished reading from the database you use the
destructor (e.g. del <some_instance>) to close the connection.

Examples in main function...
"""

DB_PATH = "../Data/world-development-indicators/database.sqlite"

class DatabaseReader(object):
    def __init__(self, path=DB_PATH):
        # Open connection and cursor
        print "Connection to DB at", path
        self.conn = sqlite3.connect(path, check_same_thread = False)
        self.conn.text_factory = str 
        self.c = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    """
    Get a particular country's data over a set of years. If you provide a 
    dateRange make it as a tuple of two integers (e.g. (1960, 1999)). Note
    that this range is inclusive.

    Returns a matrix with the data and a dictionary describing what each
    of the columns represents.
    """
    def fetchCountryData(self, countryName, dateRange = (1960, 2015)):
        # Figure out how big the matrix needs to be
        query = "SELECT COUNT(DISTINCT IndicatorName)" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + countryName + "\""
        for c in  self.c.execute(query):
            cols = int(c[0])
        print cols

        dataMatrix = np.zeros((dateRange[1] - dateRange[0] + 1, cols))
        colDictionary = {}
        
        # Read data from DB
        query = "SELECT Year, Value, IndicatorName" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + countryName + "\"" \
                + " AND Year >= " + str(dateRange[0]) \
                + " AND Year <= " + str(dateRange[1]) \
                + " ORDER BY IndicatorName"

        # Fill out matrix and dictionary
        currCol = 0
        prevIndicator = ""
        for row in self.c.execute(query):
            if row[2] != prevIndicator:
                colDictionary[currCol] = row[2]
                currCol += 1
                prevIndicator = row[2]
            dataMatrix[(int(row[0]) - dateRange[0]), currCol - 1] = row[1]
        
        return dataMatrix, colDictionary

if __name__ == '__main__':
    db = DatabaseReader()
    mat, d = db.fetchCountryData("United States", (2010, 2015))
    print mat
    del db


