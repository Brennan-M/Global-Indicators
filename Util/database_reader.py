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
NUM_COUNTRIES = 247


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
    def fetchCountryData(self, countryName, dateRange = (START_DATE, END_DATE),
            asNumpyMatrix = True):
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

        if asNumpyMatrix:
            dataMatrix = np.asmatrix(dataMatrix)

        return dataMatrix, colDictionary, attributeCodeDictionary

    """
    Get a number of attributes for a specific year. Here, the countries are on
    the rows, and the attributes are on the columns. This will return a numpy
    matrix, a row dictionary (maps indexes to country name), and a col dictionary
    """
    def fetchAttributesData(self, attributes, year):
        if type(attributes) != list:
            raise AttributeError("attributes must be a list")

        numCountries = self.countNumberCountries()
        mat = np.asmatrix(np.empty((numCountries, len(attributes))))
        mat[:] = np.NAN
        rowDic = {} # Rows represent countries
        colDic = {} # Columns represent attributes

        # Assemble queries to construct the matrix
        for col, attr in enumerate(attributes):
            colDic[attr] = col

            query = "SELECT CountryName, Value" \
                    + " FROM Indicators" \
                    + " WHERE IndicatorName = \"" + attr + "\"" \
                    + " AND YEAR = " + str(year) + ";"

            for row in self.cursor.execute(query):
                currCountry = row[0]
                currVal = row[1]

                if currCountry in rowDic.keys():
                    mat[rowDic[currCountry], col] = currVal
                else:
                    foundRow = False
                    for potentialRow in range(numCountries):
                        if potentialRow not in rowDic.values():
                            rowDic[currCountry] = potentialRow
                            mat[potentialRow, col] = currVal
                            foundRow = True
                            break
                    if not foundRow:
                        raise RuntimeError("Something went wronge while" \
                                + " forming the matrix hmm...")

        # Inverse row and column dictionaries
        # courtesy of http://stackoverflow.com/questions/483666/python-reverse-inverse-a-mapping
        highestOccupiedRow = max(rowDic.values())
        rowDic = {v: k for k, v in rowDic.items()}
        colDic = {v: k for k, v in colDic.items()}

        # Chop off rows that have no information we should just be able to
        # find the highest row that is occupied and chop after since we look
        # for room in the matrix starting at the bottom
        return mat[:highestOccupiedRow + 1,:], rowDic, colDic


    """
    Constructs a matrix for a single attribute over several different years for
    all countries. In the matrix each row is a country and each column is a year
    """
    def fetchAttributeOverTimeData(self, attribute, \
            dateRange = (START_DATE, END_DATE)):
        if type(attribute) != str:
            raise AttributeError("The attribute passed must be a string.")

        numCountries = self.countNumberCountries()
        mat = np.asmatrix(np.empty((numCountries, dateRange[1] - dateRange[0] + 1)))
        mat[:] = np.NAN
        rowDic = {} # Rows represent countries
        colDic = {} # Columns represent years

        # Fill in colDic
        for col, year in enumerate(range(dateRange[0], dateRange[1] + 1)):
            colDic[col] = year

        query = "SELECT CountryName, Year, Value" \
                + " FROM Indicators" \
                + " WHERE IndicatorName = \"" + attribute + "\"" \
                + " AND Year >= " + str(dateRange[0]) \
                + " AND Year <= " + str(dateRange[1]) + ";"

        for row in self.cursor.execute(query):
            currCountry = row[0]
            currYear = row[1]
            currVal = row[2]

            if currCountry in rowDic.keys():
                mat[rowDic[currCountry], currYear - dateRange[0]] = currVal
            else:
                foundRow = False
                for potentialRow in range(numCountries):
                    if potentialRow not in rowDic.values():
                        rowDic[currCountry] = potentialRow
                        mat[potentialRow, currYear - dateRange[0]] = currVal
                        foundRow = True
                        break
                if not foundRow:
                    raise RuntimeError("Something went wronge while" \
                            + " forming the matrix hmm...")

        #Inverse row dictionary
        highestOccupiedRow = max(rowDic.values())
        rowDic = {v: k for k, v in rowDic.items()}

        return mat[:highestOccupiedRow + 1,:], rowDic, colDic


    def countNumberCountries(self):
        query = "SELECT COUNT(DISTINCT CountryCode)" \
                + " FROM Country;"
        for row in self.cursor.execute(query):
            return int(row[0])


def testFetchcountryData(db):
    mat, d, d2 = db.fetchCountryData("United States", (2010, 2015))
    print mat
    print d

def testCountNumberCountries(db):
    print db.countNumberCountries()

def testFetchAttributeData(db):
    attrs = ["Access to electricity (% of population)",  \
            "Access to non-solid fuel (% of population)", \
            "Adequacy of social insurance programs (% of total welfare of beneficiary households)"]
    mat, rows, cols = db.fetchAttributesData(attrs, 2000)
    print mat, rows, cols
    print mat.shape

def testFetchAttributeOverTimeData(db):
    attr = "Access to electricity (% of population)"
    mat, rows, cols = db.fetchAttributeOverTimeData(attr)
    print mat, rows, cols
    print mat.shape

if __name__ == '__main__':
    db = DatabaseReader()
    # testFetchcountryData(db)
    testFetchAttributeOverTimeData(db)
    del db
