import os
import youbike
import weather
import util

dir = [f"./data_Youbike/{d}" for d in os.listdir("./data_Youbike/json") if os.path.isdir(f"./data_Youbike/json/{d}")]

os.chdir("data_Youbike")
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
util.generateDistanceCsv("final/Youbike.csv", "final/Youbike.csv", "final/Youbike.csv")

os.chdir("..")