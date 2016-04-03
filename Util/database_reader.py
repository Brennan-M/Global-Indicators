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
START_DATE = 1960
END_DATE = 2014


class DatabaseReader(object):
    def __init__(self, path=DB_PATH):
        # Open connection and cursor print "Connection to DB at", path
        self.conn = sqlite3.connect(path, check_same_thread = False)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    """
    Get a particular country's data over a set of years. If you provide a
    date_range make it as a tuple of two integers (e.g. (1960, 1999)). Note
    that this range is inclusive.

    Returns a matrix with the data and a dictionary describing what each
    of the columns represents. If there is no entry in the DB for an
    attribute it will be NaN in the matrix. These smoothed for using utitlity
    functions in Matrix_Cleaning.py
    """
    def fetchCountryData(self, countryName, dateRange = (START_DATE, END_DATE)):
        # Figure out how big the matrix needs to be
        query = "SELECT COUNT(DISTINCT IndicatorName)" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + countryName + "\"" \
                + " AND Year >= " + str(dateRange[0]) \
                + " AND Year <= " + str(dateRange[1])

        for c in  self.cursor.execute(query):
            cols = int(c[0])


        if cols == 0:
            raise RuntimeError("Invalid input, no data returned")

        dataMatrix = np.empty((dateRange[1] - dateRange[0] + 1, cols))
        dataMatrix[:] = np.NAN
        colDictionary = {}
        attributeCodeDictionary = {}

        # Read data from DB
        query = "SELECT Year, Value, IndicatorName, IndicatorCode" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + countryName + "\"" \
                + " AND Year >= " + str(dateRange[0]) \
                + " AND Year <= " + str(dateRange[1]) \
                + " ORDER BY IndicatorName"


        # Fill out matrix and dictionary
        currCol = 0
        prevIndicator = ""
        for row in self.cursor.execute(query):
            if row[2] != prevIndicator:
                colDictionary[currCol] = row[2]
                attributeCodeDictionary[row[3]] = currCol
                currCol += 1
                prevIndicator = row[2]
            dataMatrix[(int(row[0]) - dateRange[0]), currCol - 1] = row[1]
        

        return dataMatrix, colDictionary, attributeCodeDictionary


# if __name__ == '__main__':
#     db = DatabaseReader()
#     mat, d = db.fetchCountryData("United States", (2010, 2015))
#     print mat
#     print d
#     del db
