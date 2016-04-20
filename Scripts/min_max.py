import sys
import subprocess
import webbrowser
sys.path.append('../Visualization')

from visuals import Visualize


visual = Visualize()
visual.min_max_graph("NY.GDP.MKTP.KD.ZG", 0)  # NY.GDP.MKTP.KD.ZG - For Growth Rate of GDP, NY.GDP.MKTP.CD - For GDP
	#1 to normalize over all years, 0 to normalize by year
visual.start()
