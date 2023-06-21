import json
import os
import requests
import time
import numpy as np
from geopy import distance

def generateMetadata(dir, filename, idCol, infoCol):
    metadataDict = dict()
    for d in dir:
        if os.path.isfile(f"{d}/{filename}.json") == False:
            continue
        with open(f"{d}/{filename}.json","r") as file:
            data = json.load(file)
            for item in data:
                metadataDict[item[idCol]] = [item[col] for col in infoCol]
    
    metadataJson = []
    infoCol = [col if col != "lon" else "lng" for col in infoCol]
    for key, value in metadataDict.items():
        dict1 = {idCol: key}
        dict2 = {col:value[idx] for idx,col in enumerate(infoCol)}
        metadataJson.append({**dict1, **dict2})

    with open(f"final/{filename}.json","w") as file:
        json.dump(metadataJson, file)
        file.close()

def generateNearestListbyCategory(category):
    with np.load(f"final/youbike_{category}_distance.npz") as data:
        arr = data["x"]
    neareatList = []
    for col in arr:
        nidx = 0
        for j in range(len(col)):
            if col[j] < col[nidx]:
                nidx = j
        neareatList.append(nidx)
    return neareatList

def generateNearestList():
    rainfallList =  generateNearestListbyCategory("rainfall")
    tempertureList = generateNearestListbyCategory("temperture")
    nearestList = [[rainfallList[i], tempertureList[i]] for i in range(len(rainfallList))]
    return nearestList

def getCSV(url, filename):
    res = requests.get(url)
    with open(filename, "w", encoding="utf8") as file:
        file.write(res.text)

def generateDistanceCsv(lhs, rhs, outfile):
    lhs = loadData(lhs)
    rhs = loadData(rhs)

    f = open(outfile, "w")

    f.write("from,to,cost\n")
    for i, c1 in enumerate(lhs):
        for j, c2 in enumerate(rhs):
            if (i != j):
                res = distance.distance((c1['lat'], c1['lng']), (c2['lat'], c2['lng'])).km
                f.write(f"{i},{j},{res}\n")

def loadData(filename):
    try:
        with open(filename,"r") as file:
            data = json.load(file)
            file.close()
        assert (len(data) > 0)
    except:
        return None
    return data

def loadIdDict(filename, key):
    idDict = {item[key]: idx for idx, item in enumerate(loadData(filename))}
    return idDict

def valueTransform(val, L, R, defalut):
    if val >= L and val <= R:
        return val
    return defalut

def abnormalValueHandle(infile, outfile):
    with np.load(infile) as data:
        final = data['data']
        shape = final.shape
        for i in range(shape[0]):
            for j in range(shape[1]):
                for k in range(shape[2]):
                    if final[i][j][k] < 0:
                        final[i][j][k] = final[i-1][j][k]
    np.savez_compressed(outfile, data=final)
