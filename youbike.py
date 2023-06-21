import requests
import json
import numpy as np
import os
import util
import datetime as dt
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

def getNearestList(youbike, youbikeIdDict, rhs, rhsIdDict, distanceMatrix):
    nearestList = [0 for i in range(len(youbikeIdDict))]
    for i, c1 in enumerate(youbike):
        m = youbikeIdDict[c1["sno"]]
        x, minValue = 0, 10000
        for j, c2 in enumerate(rhs):
            n = rhsIdDict[c2["locationName"]]
            if distanceMatrix[m][n] < minValue:
                x, minValue = j, distanceMatrix[m][n]
        nearestList[m] = x

    return nearestList

def generateFinalMatrix(dir):
    youbikeIdDict = util.loadIdDict("final/youbike.json", "sno")
    rainfallDict = util.loadIdDict("final/rainfall.json", "locationName")
    tempertureDict = util.loadIdDict("final/temperture.json", "locationName")
    with np.load(f"final/youbike_rainfall_distance.npz") as data:
        rainfallDistanceMatrix = data["x"]
    with np.load(f"final/youbike_temperture_distance.npz") as data:
        tempertureDistanceMatrix = data["x"]
    final = np.zeros((len(dir), len(youbikeIdDict), 7))

    for i in range(len(dir)):
        youbikeData = util.loadData(f"{dir[i]}/youbike.json") or util.loadData(f"{dir[i-1]}/youbike.json")
        rainfallData = util.loadData(f"{dir[i]}/rainfall.json") or util.loadData(f"{dir[i-1]}/rainfall.json")
        tempertureData = util.loadData(f"{dir[i]}/temperture.json") or util.loadData(f"{dir[i-1]}/temperture.json")

        rainfallNearestList = getNearestList(youbikeData, youbikeIdDict, rainfallData, rainfallDict, rainfallDistanceMatrix)
        tempertureNearestList = getNearestList(youbikeData, youbikeIdDict, tempertureData, tempertureDict, tempertureDistanceMatrix)

        nowDay, nowTime = dir[i][0:8], int(dir[i][8:10]) + int(dir[i][10:12]) / 60
        nowDay = int(dt.datetime.strptime(nowDay,'%Y%m%d').date().weekday())

        for item in youbikeData:
            j = youbikeIdDict[item["sno"]]
            rainfallIdx, tempertureIdx = rainfallNearestList[j], tempertureNearestList[j]
            
            # remaining space, 10 mins rainfall, 1 hour rainfall, 3 hours rainfall, temperture, weekday, hours
            final[i][j][0] = util.valueTransform(item["sbi"], 0, item["tot"], final[i - 1][j][0] if i > 0 else 0)
            final[i][j][1] = util.valueTransform(rainfallData[rainfallIdx]["MIN_10"], 0, 50, 0)
            final[i][j][2] = util.valueTransform(rainfallData[rainfallIdx]["RAIN"], 0, 210, 0)
            final[i][j][3] = util.valueTransform(rainfallData[rainfallIdx]["HOUR_3"], 0, 600, 0)
            final[i][j][4] = util.valueTransform(tempertureData[tempertureIdx]["TEMP"], 5, 45, final[i - 1][j][4] if i > 0 else 0)
            final[i][j][5] = nowDay
            final[i][j][6] = nowTime
            
    np.savez_compressed(f"final/Youbike.npz", data = final)
 
if __name__ == "__main__":
    getData()