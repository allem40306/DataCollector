import os
import youbike
import weather
import util

dir = [f"{d}" for d in os.listdir("./data") if os.path.isdir(f"./data/{d}") and "final" not in d]

os.chdir("data")
try:
    os.mkdir("final")
except:
    pass

def generateMetadata():
    util.generateMetadata(dir, "youbike", "sno", ["lat","lng","tot"])
    util.generateMetadata(dir, "temperture", "locationName", ["lat","lon"])
    util.generateMetadata(dir, "rainfall", "locationName", ["lat","lon"])

generateMetadata()

for category in ["youbike", "rainfall", "temperture"]:
    youbike.generateDistanceMatrix(category)

youbike.generateFinalMatrix(dir)

os.chdir("..")