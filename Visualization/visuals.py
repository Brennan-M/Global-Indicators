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
from generate_regression_data import RegressionModel

app = Flask(__name__)


class MinMaxForm(Form):
   attribute = TextField("Attribute Code", [validators.Required("Please select an attribute to analyze.")])
   normalizationMethod = SelectField("Normalization Option", choices=[('min-max', "Normalize By Year"), ('global-min-max', "Normalize By Aggregate")], validators=[validators.Required("Please select a normalization technique.")])
   smoothingMethod = SelectField("Smoothing Option", choices=[('average', "Smooth By Average"), ('interpolation', "Smooth By Interpolation"), ('replacement', "Smooth By Constant (0)")], validators=[validators.Required("Please select a smoothing technique.")])

class CorrelationForm(Form):
	attribute2 = TextField("Attribute Code", [validators.Required("Please select an attribute to analyze.")])
	country = TextField("Country", [validators.Required("Please select a country.")])

class ClusterForm(Form):
	attributes = TextField("Attributes, Comma Separated", [validators.Required("Please select attributes to analyze.")])
	clusterTechnique = SelectField("Cluster Technique", choices=[('spectral', "Spectral"), ('kmeans', "K-Means")])
	kvalue = IntegerField("Cluster Count", [validators.Required("Please specify a k-count.")])
	year = IntegerField("Year", [validators.Required("Please specify a year.")])

class RegressionForm(Form):
	regressionAttribute = TextField("Attribute To Model", [validators.Required("Please select an attribute to build a regression model for.")])
	country = TextField("Country", [validators.Required("Please select a country.")])
	predictingAttributes = TextField("Attributes To Predict On, Comma Separated", [validators.Required("Please select attributes to include in the model.")])


@app.route("/", methods=["GET", "POST"])
def index():
	mmForm = MinMaxForm(request.form)
	cForm = CorrelationForm(request.form)
	clusterForm = ClusterForm(request.form)
	regressionForm = RegressionForm(request.form)
   	rd = RetrieveData()
	rd.getIndicators()
	rd.getCountries()

	if request.method == 'POST':
		if mmForm.validate() and request.form['minmax'] == 'Visualize Global Data':
			return min_max_view(request.form['attribute'], request.form['normalizationMethod'], rd.indicatorData[request.form['attribute']], request.form['smoothingMethod'])
		elif cForm.validate() and request.form['correlation'] == 'Calculate Correlations':
			return correlation_view(request.form['attribute2'], request.form['country'], rd.indicatorData)
		elif clusterForm.validate() and request.form['cluster'] == 'Cluster':
			return cluster_view(request.form['attributes'], request.form['kvalue'], request.form['clusterTechnique'], request.form['year'], rd.indicatorData)
		elif regressionForm.validate() and request.form['regression'] == 'Regression':
			return regression_view(request.form['regressionAttribute'], request.form['country'], request.form['predictingAttributes'])
		else:
			return render_template('index.html', form4 = regressionForm, form3 = clusterForm, form2 = cForm, form = mmForm, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))
	elif request.method == 'GET':
		return render_template('index.html', form4 = regressionForm, form3 = clusterForm, form2 = cForm, form = mmForm, data=json.dumps(rd.indicatorData), countries=json.dumps(rd.countryData))


@app.route("/regression", methods=["GET", "POST"])
def regression_view(attributeToModel, country, predictionAttributes):
	# Michael, You should use the attributes passed in here
	# as the parameters to your regression class

	# predictionAttributes when passed in is a comma separated string
	# so I convert it to a python array so it is easy for you to use.
	# The array, as you can see when it is printed out, is in Unicode
	# so you may need to convert this, not quite sure
	predictionAttributes = predictionAttributes.split(",")
	predictionAttributes = [x.strip() for x in predictionAttributes]

	print attributeToModel
	print country
	#print predictionAttributes
	attributeToModel = attributeToModel.encode('UTF8')
	predictionAttributes = [x.encode('UTF8') for x in predictionAttributes]
	print predictionAttributes

	model = RegressionModel(attributeToModel, country)
	polydata = model.polynomial(2, predictionAttributes)
	# model.polynomial["attributes"] = predictionAttributes
	# model.polynomial["degree"] = 2

	# When it is in dictonary form, you can pass it to the html
	# using json.dumps(YOUR DATA), see examples below
	return render_template("regression.html", polydata=json.dumps(polydata))


@app.route("/cluster", methods=["GET", "POST"])
def cluster_view(attributes, kvalue, clusterTechnique, year, indicatorData):

	attributeList = attributes.split(",")
	attributeList = [x.strip() for x in attributeList]

	kvalue = int(kvalue)
	year = int(year)
	if kvalue > 10:
		kvalue = 10
	if year < 1961:
		year = 1961
	elif year > 2014:
		year = 2014

	cluster = Cluster(attributeList, kvalue, year, clusterTechnique)
	cluster.clusterData["attributes"] = attributeList
	cluster.clusterData["year"] = year
	cluster.clusterData["kvalue"] = kvalue
	cluster.clusterData["clusterTechnique"] = clusterTechnique
	return render_template("cluster.html", indicatorData=json.dumps(indicatorData), clusterData=json.dumps(cluster.clusterData))


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
