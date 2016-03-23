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
    date_range make it as a tuple of two integers (e.g. (1960, 1999)). Note
    that this range is inclusive.

    Returns a matrix with the data and a dictionary describing what each
    of the columns represents.
    """
    def fetch_country_data(self, country_name, date_range = (1960, 2015)):
        # Figure out how big the matrix needs to be
        query = "SELECT COUNT(DISTINCT IndicatorName)" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + country_name + "\"" \
                + " AND Year >= " + str(date_range[0]) \
                + " AND Year <= " + str(date_range[1]) 

        for c in  self.c.execute(query):
            cols = int(c[0])

        data_matrix = np.zeros((date_range[1] - dateRange[0] + 1, cols))
        col_dictionary = {}
        
        # Read data from DB
        query = "SELECT Year, Value, IndicatorName" \
                + " FROM Indicators" \
                + " WHERE CountryName = \"" + country_name + "\"" \
                + " AND Year >= " + str(date_range[0]) \
                + " AND Year <= " + str(date_range[1]) \
                + " ORDER BY IndicatorName"

        # Fill out matrix and dictionary
        curr_col = 0
        prev_indicator = ""
        for row in self.c.execute(query):
            if row[2] != prev_indicator:
                col_dictionary[curr_col] = row[2]
                curr_col += 1
                prev_indicator = row[2]
            data_matrix[(int(row[0]) - date_range[0]), curr_col - 1] = row[1]
        
        return data_matrix, col_dictionary

if __name__ == '__main__':
    db = DatabaseReader()
    mat, d = db.fetch_country_data("United States", (2010, 2015))
    print mat
    del db


