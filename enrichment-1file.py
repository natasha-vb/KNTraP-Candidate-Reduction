import numpy as np 
import pandas as pd 
import glob 

filepath = glob.glob("*.clusters")
file = open(filepath, "r")
filedata = file.read()
print(filedata)
