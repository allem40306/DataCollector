import requests
import json


def getData(config):
    dataIn = json.loads(requests.get(f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-{ config['queryID'] }-001?Authorization=CWB-0D389C80-AB4C-4DE4-B6D4-DCC8EB71D8E8").text)["records"]["location"]
    dataOut = []

    for item in dataIn:
        metedata = {parameter: item[parameter] for parameter in ["lat","lon","locationName"]}
        weather = {parameter["elementName"]:parameter["elementValue"] for parameter in item["weatherElement"]}
        metedata.update({parameter: max(float(weather[parameter]),0.0) for parameter in config['parameter']})
        city = {parameter["parameterName"]:parameter["parameterValue"] for parameter in item["parameter"]}["CITY"]
        if city != "臺北市":
            continue
        dataOut.append(metedata)

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