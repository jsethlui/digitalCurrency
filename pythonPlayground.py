
import curses
import os
import sys
import requests
import time as t
import pyrebase
from datetime import datetime

# global data
idBase = ""
apiKey = ""
userHasKey = False
rateMapping = {"DOGE": "Dogecoin", 
                "ETH": "Ethereum", 
                "BTC": "Bitcoin", 
                "LTC": "Litecoin"}              

def checkModules():
    try:
        print("asdf")
        # import curses
        # import os
        # import sys
        # import requests
        # import time as t
        # import subprocess
        # from datetime import datetime
        # from firebase_admin import db 
    except ImportError:
        pass

def getCryptoCurrencyPrice(cryptoBase):
    url = "https://rest.coinapi.io/v1/exchangerate/" + str(cryptoBase) + "/USD"
    header = {"X-CoinAPI-Key": apiKey}
    response = requests.get(url, headers = header)
    responseJson = response.json()
    statusCode = response.status_code
    if (statusCode == 429):   # too many requests
        sys.stderr.write(Color.FAIL + "Error: " + Color.END + "max requests exceeded (status code = " + str(statusCode) + ")\n")
        sys.exit(1)
    return responseJson

def setApiKey(name = "Default"):
    global apiKey
    config = {
        "apiKey": "",
        "authDomain": "",
        "databaseURL": "https://getcrypto-2ab92-default-rtdb.firebaseio.com/",
        "storageBucket": ""
    }  
    firebase = pyrebase.initialize_app(config)
    database = firebase.database()
    data = database.child("Default").get()
    apiKey = data.val()["Key"]

def getTime():
    currentDate = datetime.now().strftime("%d/%m/%Y")
    currentTime = datetime.now().strftime("%I:%M:%S %p")
    return (currentDate, currentTime)

def main(argv):
    try:
        global idBase
        idBase = sys.argv[1]                # id base
    except IndexError:          # when no argument specified
        message  = "\033[1m" + "Usage: " + "\033[0m" + "pythonPlayground "
        for key in rateMapping.keys():
            temp  = "[" + str(key) + "] "
            message += temp
        sys.stderr.write(message + "\n")
        sys.exit(1)
 
    # checking if valid currency base
    if idBase not in rateMapping.keys():
        sys.stderr.write("\033[1m" + "Error: " + "\033[0m" + "invalid mapping " + str(idBase) +  "\n")
        sys.exit(1)

    setApiKey()     # set to default key
    curses.wrapper(cursesMain)
    sys.exit(0)

def cursesMain(window):
    global idBase
    global userHasKey
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    window.bkgd(1, curses.color_pair(1))
    window.nodelay(True)        # enable refreshing  
    maxX = window.getmaxyx()[0] # get max y
    maxY = window.getmaxyx()[1] # get max x
    currentRow = 5

    # instantiating bar
    bar = ""
    for i in range(63):
        bar += "-"

    refreshRate = 840   # fourteen minutes
    timeElapsed = refreshRate
    t.sleep(1 - (t.time() % 1))
    while (True):
        window.timeout(1000)        # block every second

        # user info
        if ((userHasKey == False) and (apiKey != "")):
            window.addstr(0, maxY - 12, "Default Key", curses.A_BOLD)
        elif ((userHasKey == True) and (apiKey == "")):
            window.addstr(0, maxY - 15, "Registered Key", curses.A_BOLD)

        # crypto base 
        window.addstr(2, 1, "Currency: ", curses.A_BOLD)
        window.addstr(2, 11, rateMapping.get(idBase) + " (" + idBase + ")")

        # refresh rate
        window.addstr(2, 31, "Refresh Rate: ", curses.A_BOLD)
        window.addstr(2, 45, str(int(refreshRate)) + " seconds")
        window.addstr(2, 45, "(" + str(int(refreshRate / 60)) + " minutes)")

        # time elapsed
        window.addstr(2, 61, "Time Elapsed: ", curses.A_BOLD)
        window.addstr(2, 75, str(timeElapsed) + " / " + str(refreshRate) + " seconds")
        window.addstr(3, 75, str(round(timeElapsed / refreshRate, 4) * 100) + " %")
        timeElapsed -= 1
        if (timeElapsed < 0):
            timeElapsed = refreshRate

        # drawing table labels
        window.addstr(3, 1, "Date           Time           Rate (USD)           Status", curses.A_BOLD)
        window.addstr(4, 1, bar, curses.A_BOLD)

        # drawing rows
        date = getTime()[0]
        time = getTime()[1]
        window.addstr(currentRow, 1, date)
        window.addstr(currentRow, len(date) + 1, "\t" + time)
        window.addstr(currentRow, len(date) + 1 + len(time) + len("         "), "10")
        currentRow += 1
        if (currentRow == 23):   # 20 + 3 = 23
            currentRow = 5

        # settings 
        window.addstr(maxX - 1, maxY - 11, "(SETTINGS)", curses.A_BOLD | curses.A_REVERSE | curses.A_STANDOUT)

        # quit
        window.addstr(maxX - 1, 0, "(QUIT)", curses.A_BOLD | curses.A_REVERSE | curses.A_STANDOUT)
        window.refresh()
        userChar = window.getch()

        if (userChar == ord("q") or (userChar == ord("Q"))):
            curses.endwin()
            break
        elif (userChar == ord("s") or (userChar == ord("S"))):
            curses.endwin()
            break
        window.clear()

if __name__ == "__main__":
    main(sys.argv[1:])
