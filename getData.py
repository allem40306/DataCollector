import argparse
import os
import time
from datetime import datetime,timezone,timedelta
import weather
import youbike

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="test program")
    args = parser.parse_args()

    interval = 5 if args.test else 300

    try:
        os.mkdir("data")
    except:
        pass
    os.chdir("data")

    while True:
        t = time.time()

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

        t = time.time() - t
        time.sleep(interval - t)
        
        os.chdir("..")
