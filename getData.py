import os
import time
from datetime import datetime,timezone,timedelta
import weather
import youbike

if __name__ == "__main__":

    try:
        os.mkdir("data")
    except:
        pass
    os.chdir("data")

    while True:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = now.astimezone(timezone(timedelta(hours=8)))
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
