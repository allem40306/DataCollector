import requests
import json
import numpy as np
import os
import util
from geopy import distance

def getData():
    inData = json.loads(requests.get("https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json").text)
    outData = []
    parameterList = ["sno", "lat", "lng", "tot", "sbi"]
    for item in inData:
        try:
            tmp = {parameter: item[parameter] for parameter in parameterList}
            outData.append(tmp)
        except:
            pass
    with open("youbike.json", "w") as file:
        json.dump(outData, file)

def generateDistanceMatrix(dataField):
    lhs = util.loadData(f"final/youbike.json")
    rhs = util.loadData(f"final/{dataField}.json")
    distanceMatrix = np.zeros([len(lhs), len(rhs)])

    for i, c1 in enumerate(lhs):
        for j, c2 in enumerate(rhs):
            distanceMatrix[i][j] = distance.distance((c1['lat'], c1['lng']), (c2['lat'], c2['lng'])).km

    np.savez_compressed(f"final/youbike_{dataField}_distance.npz", x=distanceMatrix)

def valueTransform(val, L, R):
    if val >= L and val <= R:
        return val
    return -100

def generateFinalMatrix(dir):
    youbikeIdDict = util.loadIdDict("youbike")
    nearestList = util.generateNearestList()
    final = np.zeros((len(dir), len(youbikeIdDict), 5))
    for i in range(len(dir)):
        youbikeData = util.loadData(f"{dir[i]}/youbike.json")
        rainfallData = util.loadData(f"{dir[i]}/rainfall.json")
        tempertureData = util.loadData(f"{dir[i]}/temperture.json")
        for item in youbikeData:
            j = youbikeIdDict[item["sno"]]
            rainfallIdx, tempertureIdx = [int(idx) for idx in nearestList[j]]
            final[i][j][0] = valueTransform(item["sbi"], 0, item["tot"])
            final[i][j][1] = valueTransform(rainfallData[rainfallIdx]["MIN_10"], 0, 50)
            final[i][j][2] = valueTransform(rainfallData[rainfallIdx]["RAIN"], 0, 210)
            final[i][j][3] = valueTransform(rainfallData[rainfallIdx]["HOUR_3"], 0, 600)
            final[i][j][4] = valueTransform(tempertureData[tempertureIdx]["TEMP"], 5, 45)
    print(final.shape)
    np.savez_compressed(f"final/final.npz", x = final)
 
if __name__ == "__main__":
    getData()