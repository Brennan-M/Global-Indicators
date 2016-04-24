from flask import Flask, request, flash, render_template, redirect, url_for
from flask.views import View

from flask_wtf import Form
from wtforms import *

import json
import sys
sys.path.append('../Tools')

from generate_min_max_data import MinMax
from retrieve_db_data import RetrieveData
from find_correlation_data import CorrelatedIndicators
#from generate_cluster_data import Cluster

app = Flask(__name__)


class InDepthForm(Form):
   attribute = TextField("Attribute", [validators.Required("Please select an attribute to analyze.")])
   country = TextField("Country", [validators.Required("Please select a country.")])
   normalizationMethod = SelectField("Normalization Option", choices=[('nby', "Normalize By Year"), ('nba', "Normalize By Aggregate")], validators=[validators.Required("Please select a normalization technique.")])
   minMaxSubmit = SubmitField("Visualize Global Data")


@app.route("/", methods=["GET", "POST"])
def index():
	form = InDepthForm(request.form)
   	rd = RetrieveData()
	rd.getIndicators()
	rd.getCountries()
	if request.method == 'POST':
		if form.validate() == True:
			return min_max_view(request.form['attribute'], request.form['normalizationMethod'], rd.indicatorData[request.form['attribute']])
		else:
			return render_template('index.html', form = form, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))
	elif request.method == 'GET':
		return render_template('index.html', form = form, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))



@app.route("/min_max", methods=["GET", "POST"])
def min_max_view(attribute, normalizeMethod, definition):

		data = MinMax(attribute)
		if normalizeMethod == "nby":
			data.normalizeDataByYear()
		elif normalizeMethod == "nba":
			data.normalizeData()
		data.organizedInfo['attributeAnalyzed'] = definition

		rd = RetrieveData()
		rd.getCountries()

		return render_template("min_max.html", form = form, data=json.dumps(data.organizedInfo))




def start():
	app.secret_key = 'flask key'
	app.run(host='0.0.0.0', port=3000, debug=True)


if __name__ == "__main__":
	start()


'''
	def cluster_graph(self, k, year, attribute, clusterMethod, normalizeMethod):
		@app.route("/")
		def cluster_view():
			data = Cluster(k, year, attribute)
			if normalizeMethod == 0:
				data.normalizeDataByYear()
			else:
				data.normalizeData()

			if clusterMethod == "kmeans":
				data.kmeans()
			elif clusterMethod == "dbscan":
				data.dbscan()
			return render_template("cluster.html", data=json.dumps(data.clusterInfo))
'''

