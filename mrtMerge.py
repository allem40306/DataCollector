import os
import requests
import json
import urllib
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from geopy import distance
import util
import mrt
import weather

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

def generateFinalMatrix(day):
    mrt.json2npz(day)
    weather.monthlyStationsRecord(day)

    beginDay = day
    endDay = day + relativedelta(months=1)
    month = str(day)[:7].replace("-", "")
    numOfday = int((endDay - beginDay).days)

    try:
        os.mkdir("final")
    except:
        pass
    
    weatherRecord = util.loadData(f"weatherRecord/{month}.json")
    
    with np.load(f"mrtFlowNpz/{month}.npz") as data:
        mrtFlow = data['x']
    numOfTime = mrtFlow.shape[0]
    numOfStation = mrtFlow.shape[1]

    final = np.zeros([numOfTime, numOfStation, 6])

    # inflow, outflow, rain, temp, weekday, hours
    for i in range(numOfday):
        iteratedDay = beginDay + relativedelta(days=i)
        weekday = iteratedDay.weekday()
        print(f"finalMatrix: {iteratedDay}")
        for j in range(24):
            timeStamp = i * 24 + j
            inFlow = np.sum(mrtFlow[timeStamp], axis=0)
            outFlow = np.sum(mrtFlow[timeStamp], axis=1)
            rain, temp = getNearestWeatherInfo(weatherRecord[i][j])
            for k in range(numOfStation):
                final[timeStamp][k][0] = max(inFlow[k], 0)
                final[timeStamp][k][1] = max(outFlow[k], 0)
                final[timeStamp][k][2] = util.valueTransform(rain[k], 0, 210)
                final[timeStamp][k][3] = util.valueTransform(temp[k], -5, 45)
                final[timeStamp][k][4] = weekday
                final[timeStamp][k][5] = j + 1

    np.savez_compressed(f"final/{month}.npz", x=final)

if __name__ == "__main__":
    os.chdir("data_MRT")

    # mrt.getCsv()
    mrt.getStation()
    weather.weatherStation()

    day = dt.datetime.strptime('2017-01-01','%Y-%m-%d').date()
    endDay = dt.datetime.strptime('2023-03-31','%Y-%m-%d').date()

    try:
        os.mkdir("weatherRecord")
    except:
        pass

    while day <= endDay:
        generateFinalMatrix(day)
        day = day + relativedelta(months=1)
