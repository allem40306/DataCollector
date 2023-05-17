import requests
import json
import urllib
import datetime as dt
import util
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

def weatherStation():
    url = f"https://e-service.cwb.gov.tw/wdps/obs/state.htm#existing_station"
    res = requests.get(url)
    res.encoding = "utf8"
    soup = BeautifulSoup(res.text, 'html.parser')
    
    stations = []
    for idx, item in enumerate(soup.find_all("tr")):
        tmp = str(item)
        if 'tr class' in tmp:
            continue
        tmp = tmp.replace("\n", "").replace("</td><td>", ",").replace("<tr>", "").replace("</tr>", "").replace("<td>", "").replace("</td>", "")
        tmp = tmp.split(",")
        if tmp[6] != "臺北市" and tmp[6] != "新北市":
            continue
        tmp = {"sno": tmp[0],"name": tmp[1], "height": tmp[3], "lat": tmp[5], "lng": tmp[4], "from": tmp[8], "to": tmp[9]}
        stations.append(tmp)
    with open("weatherStation.json", "w") as file:
        json.dump(stations, file)
        file.close()
    print("save weatherStation.json")

def dailyStationRecord(day, station):
    location = urllib.parse.quote(station["name"])
    location = urllib.parse.quote(location)

    url = f"https://e-service.cwb.gov.tw/HistoryDataQuery/DayDataController.do?command=viewMain&station=466910&stname={ location }&datepicker={ day }&altitude={ station['height'] }m"
    res = requests.get(url)
    res.encoding = "utf8"
    weatherRecord = []
    soup = BeautifulSoup(res.text, 'html.parser')
    
    for idx, item in enumerate(soup.find_all("tr")):
        tmp = str(item)
        if idx == 0 or 'tr class' in tmp:
            continue
        tmp = tmp.replace("\n", "").replace("</td><td>", ",")
        for w in ["<tr>", "</tr>", "<td>", "</td>", '<td nowrap="">', "\xa0"]:
            tmp = tmp.replace(w, "")
        for w in ["T", "&"]:
            tmp = tmp.replace(w, "0.0")
        for w in ["x", "/", "...", "V"]:
            tmp = tmp.replace(w, "-100")
        tmp = tmp.split(",")
        weatherRecord.append({"hour": tmp[0], "TEMP": float(tmp[3]), "RAIN": float(tmp[10])})
    return weatherRecord

def monthlyStationsRecord(day):
    beginDay = day
    endDay = day + relativedelta(months=1)
    month = str(day)[:7].replace("-", "")
    
    stations = util.loadData("weatherStation.json")
    monthRecord = []
    while beginDay < endDay:
        print(f"StationsRecord: {beginDay}")
        dayRecord = [[] for i in range(24)]
        for station in stations:
            if (station["from"] <= str(beginDay) and (station["to"] == "" or str(beginDay) <= station["to"])) == False:
                continue
            stationRecord = dailyStationRecord(beginDay, station)
            for record in stationRecord:
                dayRecord[int(record["hour"]) - 1].append({"station": station["name"], "TEMP": record["TEMP"],"RAIN": record["RAIN"]})
        monthRecord.append(dayRecord)
        beginDay = beginDay + dt.timedelta(days=1)

    with open(f"weatherRecord/{month}.json", "w") as file:
        json.dump(monthRecord, file)
    print(f"save weatherRecord/{month}.json")

def getData(config):
    dataIn = json.loads(requests.get(f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-{ config['queryID'] }-001?Authorization=CWB-0D389C80-AB4C-4DE4-B6D4-DCC8EB71D8E8").text)["records"]["location"]
    dataOut = []

    for item in dataIn:
        try:
            city = {parameter["parameterName"]:parameter["parameterValue"] for parameter in item["parameter"]}["CITY"]
            if city != "臺北市":
                continue

            metedata = {parameter: item[parameter] for parameter in ["lat","lon","locationName"]}
            weather = {parameter["elementName"]:parameter["elementValue"] for parameter in item["weatherElement"]}
            metedata.update({parameter: max(float(weather[parameter]),0.0) for parameter in config['parameter']})
            dataOut.append(metedata)
        except:
            pass

    with open(f"{ config['filename'] }.json", "w") as file:
            json.dump(dataOut, file)

def getTempData():
    tempConfig = {"filename": "temperture", "queryID": "A0001", "parameter": ["TEMP"]}
    getData(tempConfig)

def getRainData():
    rainConfig = {"filename": "rainfall", "queryID": "A0002", "parameter": ["MIN_10", "RAIN", "HOUR_3"]}
    getData(rainConfig)

def main():
    getTempData()
    getRainData()

if __name__ == "__main__":
    main()