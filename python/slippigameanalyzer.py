# Import everything
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import slippi
import os
import json
import sys
import matplotlib.image as mpimg 
import matplotlib
import gc
from slippi import Game
import preprocessing as pp
import states
import populategames as popgames

# print("Begin.")
# print(os.getcwd())
# print(os.path.basename(__file__))
# print(os.path.abspath(__file__))
# print(os.path.dirname(__file__))
def convertToPortDict():
    with open(os.path.dirname(__file__) + '/slippinames.json') as file:
        myports = json.load(file)
        file.close()
    portDict = {}
    for i in range(0, len(myports)):
        portDict[myports[i]["filename"]] = myports[i]["myport"]
    del myports
    return portDict
arg = sys.argv[1]
# print(f"arg: {arg}")
try:
	popgames.populateData(convertToPortDict(), arg)
except KeyboardInterrupt:
    sys.exit()