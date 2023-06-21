import os
import csv
import requests
import json
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from geopy import distance
import util
import weather

# https://www.delftstack.com/zh-tw/howto/python/python-download-csv-from-url/
def getCsv(infile = "mrtDataUrlList.csv"):
    util.getCSV("https://data.taipei/api/dataset/63f31c7e-7fc3-418b-bd82-b95158755b4d/resource/eb481f58-1238-4cff-8caa-fa7bb20cb4f4/download", infile)

    try:
        os.mkdir("mrtFlowCsv")
    except:
        pass

    with open(infile, "r", encoding="utf8") as file:
        spamreader = csv.reader(file, delimiter=' ', quotechar='|')

        for idx, row in enumerate(spamreader):
            if idx == 0:
                continue
            url = row[0].split(",")[1]
            outfile = url.split("_")[-1]
            util.getCSV(url, f"mrtFlowCsv/{outfile}")

def getStation(infile = "mrtStationEntrance.csv", outfile = "mrtStation.json" ):
    stations = []

    if os.path.isfile(outfile):
        os.remove(outfile)

    with open(infile, "r") as file:
        for idx, line in enumerate(file.readlines()):
            if idx == 0 or line == "\n":
                continue
            data = line.split(",")
            if data[1] == "板橋站出口1":
                data[1] = "BL板橋站出口1"
            if data[1] == "板橋站出口4":
                data[1], data[2] = "Y板橋站出口1", "1"
            if (data[2]) != "0" and (data[2]) != "1" and (data[2]) != "M1":
                continue
            data = data[1].split("站")[0], data[4], data[3]
            data = {"station": data[0], "lat": data[1], "lng": data[2]}
            stations.append(data)
        file.close()

    with open(outfile, "a", encoding="utf8") as file:
        json.dump(stations, file)
        file.close()
    print(f"save {outfile}")

def json2npz(beginDay):
    endDay = beginDay + relativedelta(months=1)
    month = str(beginDay)[:7].replace("-", "")
    numOfday = int((endDay - beginDay).days)

    mrtStationDict = util.loadIdDict("mrtStation.json", "station")
    numOfStation = len(mrtStationDict)
    flowMatrix = np.zeros([numOfday * 24, numOfStation, numOfStation]) 

    try:
        os.mkdir("mrtFlowNpz")
    except:
        pass

    with open(f"mrtFlowCsv/{month}.csv", "r", encoding="utf8") as file:
        spamreader = csv.reader(file, delimiter=' ', quotechar='|')
        for idx, row in enumerate(spamreader):
            if len(row) == 0 or idx <= 0:
                continue
            data = row[0].split(',')
            if month not in "".join(data[0].split('-')):
                continue
            i = (int(data[0].split('-')[2]) - 1) * 24 + int(data[1])
            j = mrtStationDict[data[2].replace("站", "")]
            k = mrtStationDict[data[3].replace("站", "")]
            v = int(data[4])
            assert(flowMatrix[i][j][k] == 0)
            flowMatrix[i][j][k] = v

    np.savez_compressed(f"mrtFlowNpz/{month}.npz", x=flowMatrix)
    print(f"save mrtFlowNpz/{month}.npz")

def getNearestWeatherInfo(weatherRecord):
    mrtStation = util.loadData("mrtStation.json")
    mrtStationDict = util.loadIdDict("mrtStation.json", "station")

    weatherStation = util.loadData("weatherStation.json")
    weatherStationDict = util.loadIdDict("weatherStation.json", "name")
    weatherLocation = [{"lat": weatherStation[weatherStationDict[record["station"]]]["lat"], "lng": weatherStation[weatherStationDict[record["station"]]]["lng"]} for record in weatherRecord]

    rain = [0 for i in range(len(mrtStation))]
    temp = [0 for i in range(len(mrtStation))]

    for i, c1 in enumerate(mrtStation):
        rainV, rainD = 0, 100
        tempV, tempD = 0, 100

        for loc, record in zip(weatherLocation, weatherRecord):
            tmp = distance.distance((c1['lat'], c1['lng']), (loc['lat'], loc['lng'])).km
            if tmp < rainD and record["RAIN"] >= -0.1:
                rainD = tmp
                rainV = record["RAIN"]
            if tmp < tempD and record["TEMP"] >= -0.1:
                tempD = tmp
                tempV = record["TEMP"]
        
        rain[mrtStationDict[c1["station"]]] = rainV
        temp[mrtStationDict[c1["station"]]] = tempV

    return rain, temp

def generateMonthlyMatrix(beginDay):
    endDay = beginDay + relativedelta(months=1)
    month = str(beginDay)[:7].replace("-", "")
    numOfday = int((endDay - beginDay).days)

    # json2npz(beginDay)
    # weather.monthlyStationsRecord(beginDay)

    try:
        os.mkdir("final")
    except:
        pass
    
    weatherRecord = util.loadData(f"weatherRecord/{month}.json")
    
    with np.load(f"mrtFlowNpz/{month}.npz") as data:
        mrtFlow = data['x']
    
    numOfTime, numOfStation, _ = mrtFlow.shape
    final = np.zeros([numOfTime, numOfStation, 6])

    print(numOfday)
    for i in range(numOfday):
        iteratedDay = beginDay + relativedelta(days=i)
        weekday = iteratedDay.weekday()
        print(f"finalMatrix: {iteratedDay}")
        for j in range(24):
            timeStamp = i * 24 + j
            inFlow = np.sum(mrtFlow[timeStamp], axis=0)
            outFlow = np.sum(mrtFlow[timeStamp], axis=1)
            rain, temp = getNearestWeatherInfo(weatherRecord[i][j])
            
            # inflow, outflow, rain, temp, weekday, hours
            for k in range(numOfStation):
                final[timeStamp][k][0] = max(inFlow[k], 0)
                final[timeStamp][k][1] = max(outFlow[k], 0)
                final[timeStamp][k][2] = util.valueTransform(rain[k], 0, 210, 0)
                final[timeStamp][k][3] = util.valueTransform(temp[k], -5, 45, final[timeStamp - 1][k][3])
                final[timeStamp][k][4] = weekday
                final[timeStamp][k][5] = j + 1

    np.savez_compressed(f"final/{month}.npz", x=final)

def generateFinalMatrix(day, endDay):
    final = None
    
    while day < endDay:
        infile = f"final/{str(day)[0:4]}{str(day)[5:7]}.npz"
        with np.load(infile) as data:
            tmp = data['x']
            if final is None:
                final = tmp
            else:
                final = np.concatenate([final, tmp])
                print(final.shape)
        day = day + relativedelta(months=1)

    np.savez_compressed(f"final/all.npz", data=final)
