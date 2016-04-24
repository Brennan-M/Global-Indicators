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
from generate_cluster_data import Cluster

app = Flask(__name__)


class MinMaxForm(Form):
   attribute = TextField("Attribute Code", [validators.Required("Please select an attribute to analyze.")])
   normalizationMethod = SelectField("Normalization Option", choices=[('min-max', "Normalize By Year"), ('global-min-max', "Normalize By Aggregate")], validators=[validators.Required("Please select a normalization technique.")])
   smoothingMethod = SelectField("Smoothing Option", choices=[('average', "Smooth By Average"), ('interpolation', "Smooth By Interpolation"), ('replacement', "Smooth By Constant (0)")], validators=[validators.Required("Please select a smoothing technique.")])

class CorrelationForm(Form):
	attribute2 = TextField("Attribute Code", [validators.Required("Please select an attribute to analyze.")])
	country = TextField("Country", [validators.Required("Please select a country.")])
	correlationSubmit = SubmitField("Calculate Correlation Values")

class ClusterForm(Form):
	attributes = TextField("Attributes, Comma Separated", [validators.Required("Please select attributes to analyze, at least 2.")])


@app.route("/", methods=["GET", "POST"])
def index():
	mmForm = MinMaxForm(request.form)
	cForm = CorrelationForm(request.form)

   	rd = RetrieveData()
	rd.getIndicators()
	rd.getCountries()

	if request.method == 'POST':
		if mmForm.validate() and request.form['minmax'] == 'Visualize Global Data':
			return min_max_view(request.form['attribute'], request.form['normalizationMethod'], rd.indicatorData[request.form['attribute']], request.form['smoothingMethod'])
		elif cForm.validate() and request.form['correlation'] == 'Calculate Correlations':
			return correlation_view(request.form['attribute2'], request.form['country'], rd.indicatorData)
		else:
			return render_template('index.html', form2 = cForm, form = mmForm, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))
	elif request.method == 'GET':
		return render_template('index.html', form2 = cForm, form = mmForm, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))


@app.route("/correlations", methods=["GET", "POST"])
def correlation_view(attribute, country, indicatorData):
	extraInfo = {"attr":attribute, "ctry":country}
	ci = CorrelatedIndicators(attribute, country)
	ci.calculateCorrelations()
	return render_template("correlations.html", info=json.dumps(extraInfo), correlationData=json.dumps(ci.correlationValues), indicatorData=json.dumps(indicatorData))


@app.route("/min_max", methods=["GET", "POST"])
def min_max_view(attribute, normalizeMethod, definition, smoothingMethod):

    mm = MinMax()
    data = mm.generateData(attribute, normalizeMethod, smoothingMethod)
    data['attributeAnalyzed'] = definition

    return render_template("min_max.html", form = form, data=json.dumps(data))

@app.route("/cluster", methods=["GET", "POST"])
def cluster_view(yearOptions, attributes, kvalue):
	#clusterData = Cluster("2012", 5, attributes)

	return render_template("cluster.html")


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
