import sys
import subprocess
import webbrowser
sys.path.append('../Visualization')

from visuals import Visualize


visual = Visualize()
visual.min_max_graph("NY.GDP.PCAP.CD")
visual.start()
