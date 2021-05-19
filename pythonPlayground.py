
import curses
import os
import sys
import requests
from datetime import datetime

idBase = ""
rateMapping = {"DOGE": "Dogecoin", 
                "ETH": "Ethereum", 
                "BTC": "Bitcoin", 
                "LTC": "Litecoin"}

def getCryptoCurrencyPrice(cryptoBase):
    url = "https://rest.coinapi.io/v1/exchangerate/" + str(cryptoBase) + "/USD"
    apiKey = "F630E2F0-8BBC-4DDF-AE7B-41E2F54B97D2"
    header = {"X-CoinAPI-Key": apiKey}
    response = requests.get(url, headers = header)
    responseJson = response.json()
    statusCode = response.status_code
    if (statusCode == 429):   # too many requests
        sys.stderr.write(Color.FAIL + "Error: " + Color.END + "max requests exceeded (status code = " + str(statusCode) + ")\n")
        sys.exit(1)
    return responseJson

def getTime():
    currentDate = datetime.now().strftime("%d/%m/%Y")
    currentTime = datetime.now().strftime("%I:%M:%S %p")
    return (currentDate, currentTime)

def main(argv):
    try:
        global idBase
        idBase = sys.argv[1]                # id base
    except IndexError:          # when no argument specified
        message  = "\033[1m" + "Usage: " + "\033[0m" + str(sys.argv[0]) + " "       # with bold formatting
        for key in rateMapping.keys():
            temp  = "[" + str(key) + "] "
            message += temp
        sys.stderr.write(message + "\n")
        sys.exit(1)
 
    # checking if valid currency base
    if idBase not in rateMapping.keys():
        sys.stderr.write("\033[1m" + "Error: " + "\033[0m" + "invalid mapping " + str(idBase) +  "\n")
        sys.exit(1)

    curses.wrapper(cursesMain)
    sys.exit(0)

def cursesMain(window):
    global idBase

    window.nodelay(True)   # enable refreshing  
    maxX = window.getmaxyx()[0]
    maxY = window.getmaxyx()[1]

    # instantiating bar
    bar = ""
    for i in range(63):
        bar += "-"

    refreshRate = 840   # fourteen minutes
    timeElapsed = refreshRate
    while (True):
        window.timeout(1000)        # block every second

        # crypto base (top left)
        window.addstr(1, 1, "Currency: ", curses.A_BOLD)
        window.addstr(1, 11, rateMapping.get(idBase) + " (" + idBase + ")")

        # refresh rate (left of crypto base)
        window.addstr(1, 31, "Refresh Rate: ", curses.A_BOLD)
        window.addstr(1, 45, str(int(refreshRate / 60)) + " minutes")
        window.addstr(2, 45, "(" + str(int(refreshRate)) + " seconds)")

        # time elapsed
        window.addstr(1, 61, "Time Elapsed: ", curses.A_BOLD)
        window.addstr(1, 75, str(timeElapsed) + " / " + str(refreshRate) + " seconds")
        window.addstr(2, 75, str(round(timeElapsed / refreshRate, 4) * 100) + " %")
        timeElapsed -= 1
        if (timeElapsed < 0):
            timeElapsed = refreshRate

        # drawing table labels
        window.addstr(3, 1, "Date           Time           Rate (USD)           Status", curses.A_BOLD)
        window.addstr(4, 1, bar, curses.A_BOLD)

        # drawing first row
        date = getTime()[0]
        time = getTime()[1]
        window.addstr(5, 1, date)
        window.addstr(5, len(date) + 1, "\t" + time)
        window.addstr(5, len(date) + 1 + len(time) + len("         "), "10")


        # quit (bottom left)
        window.addstr(maxX - 1, 0, "(QUIT)", curses.A_BOLD | curses.A_REVERSE | curses.A_STANDOUT)
        window.refresh()
        userChar = window.getch()
        if (userChar == ord("q") or (userChar == ord("Q"))):
            curses.endwin()
            break
        window.clear()

if __name__ == "__main__":
    main(sys.argv[1:])
