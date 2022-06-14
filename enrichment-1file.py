import numpy as np 
import pandas as pd 
import glob 

filepath = glob.glob("*.clusters")
file = pd.read_csv(filepath)
print(file)
