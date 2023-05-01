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
    
    logPath = f"{os.getcwd()}\log.txt"
    f = open(logPath,"a")
    f.close()

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
        for fun in [weather.getTempData, weather.getRainData, youbike.getData]:
            try:
                fun()
            except:
                with open(logPath, "a") as f:
                    f.write(f"error: { timeStamp }_{fun.__name__}\n")
                f.close()
                pass

        t = time.time() - t
        time.sleep(interval - t)
        
        os.chdir("..")
