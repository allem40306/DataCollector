import os
import time
import datetime
import weather
import youbike

if __name__ == "__main__":

    try:
        os.mkdir("data")
    except:
        pass
    os.chdir("data")

    while True:
        now = datetime.datetime.now()
        timeStamp = now.strftime("%Y%m%d%H%M%S")

        try:
            os.mkdir(timeStamp)
        except:
            pass
        os.chdir(timeStamp)

        weather.getTempData()
        weather.getRainData()
        youbike.getData()
        time.sleep(300)
        
        os.chdir("..")
