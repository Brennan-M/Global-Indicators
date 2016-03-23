from flask import Flask
from flask.views import View
from flask import render_template, redirect
import json
import sys
sys.path.append('../Tools')

from generate_min_max_data import MinMax

app = Flask(__name__)

class Visualize:

	def welcome(self):
		@app.route("/")
		def index():
			return render_template("index.html")

	def min_max_graph(self, attribute):
		@app.route("/")
		def min_max_view():
			data = MinMax(attribute)
			return render_template("min_max.html", data=json.dumps(data.organizedInfo))

	def start(self):
		app.run(host='0.0.0.0', port=3000, debug=True)

