import os
import csv
import requests
import json
import numpy as np
import util
from dateutil.relativedelta import relativedelta

# https://www.delftstack.com/zh-tw/howto/python/python-download-csv-from-url/
def getCsv():
    infilename = "mrtDataUrlList.csv"
    util.getCSV("https://data.taipei/api/dataset/63f31c7e-7fc3-418b-bd82-b95158755b4d/resource/eb481f58-1238-4cff-8caa-fa7bb20cb4f4/download", infilename)
    with open(infilename, "r", encoding="utf8") as file:
        spamreader = csv.reader(file, delimiter=' ', quotechar='|')
        for idx, row in enumerate(spamreader):
            if idx == 0:
                continue
            url = row[0].split(",")[1]
            filename = url.split("_")[-1]
            util.getCSV(url, f"mrtFlowCsv/{filename}")

def getStation():
    infilename = "mrtStationEntrance.csv"
    outfilename = "mrtStation.json"
    util.getCSV("https://data.taipei/api/dataset/cfa4778c-62c1-497b-b704-756231de348b/resource/307a7f61-e302-4108-a817-877ccbfca7c1/download", infilename)
    if os.path.isfile(outfilename):
        os.remove(outfilename)

    stations = []
    with open(infilename, "r") as file:
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

    with open(outfilename, "a", encoding="utf8") as file:
        json.dump(stations, file)
        file.close()
    print(f"save {outfilename}")

def json2npz(day):
    beginDay = day
    endDay = day + relativedelta(months=1)
    month = str(day)[:7].replace("-", "")
    numOfday = int((endDay - beginDay).days)

    mrtStationDict = util.loadIdDict("mrtStation.json", "station")
    numOfStation = len(mrtStationDict)

    flowMatrix = np.zeros([numOfday * 24, numOfStation, numOfStation]) 
    with open(f"mrtFlowCsv/{month}.csv", "r") as file:
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
