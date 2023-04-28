import requests
import json
import numpy as np

def getData():
    inData = json.loads(requests.get("https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json").text)
    outData = []
    for item in inData:
        parameterList = ["sno", "lat", "lng", "tot", "sbi"]
        tmp = {parameter: item[parameter] for parameter in parameterList}
        outData.append(tmp)
    with open("youbike.json", "w") as file:
        json.dump(outData, file)

if __name__ == "__main__":
    getData()