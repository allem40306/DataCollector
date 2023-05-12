import json
import os
import requests
import time
import numpy as np

def generateMetadata(dir, filename, idCol, infoCol):
    metadataDict = dict()
    for d in dir:
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

def loadData(pathname):
    with open(pathname,"r") as file:
        data = json.load(file)
        file.close()
    return data

def loadIdDict(category):
    idDict = {item["sno"]: idx for idx, item in enumerate(loadData(f"final/{category}.json"))}
    return idDict