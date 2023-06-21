import os
import datetime as dt
from dateutil.relativedelta import relativedelta
import util
import mrt
import weather

os.chdir("data_MRT")

mrt.getCsv()
mrt.getStation()
weather.weatherStation()

try:
    os.mkdir("weatherRecord")
except:
    pass

day = dt.datetime.strptime('2017-01-01','%Y-%m-%d').date()
beginDay = day
endDay = dt.datetime.strptime('2017-02-01','%Y-%m-%d').date()

while beginDay < endDay:
    mrt.generateMonthlyMatrix(beginDay)
    beginDay = beginDay + relativedelta(months=1)


mrt.generateFinalMatrix(day, endDay)
util.abnormalValueHandle("final/all.npz", "final/MRT.npz")
util.generateDistanceCsv("mrtStation.json", "mrtStation.json", "MRT.csv")