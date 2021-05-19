
import curses
import subprocess
import os
import sys
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
 
    if idBase not in rateMapping.keys():
        sys.stderr.write("\033[1m" + "Error: " + "\033[0m" + "invalid mapping " + str(idBase) +  "\n")
        sys.exit(1)

    curses.wrapper(cursesMain)
    sys.exit(0)

def cursesMain(window):
    window.nodelay(True)   # enable refreshing  
    maxX = window.getmaxyx()[0]
    maxY = window.getmaxyx()[1]

    # instantiating bar
    bar = ""
    for i in range(63):
        bar += "-"

    global idBase
    while (True):
        window.timeout(1000)        # block every second

        # crypto base (top left)
        window.addstr(0, 0, "Currency: ", curses.A_BOLD)
        window.addstr(0, len("Currency: "), rateMapping.get(idBase) + " (" + idBase + ")")

        # date and time (top right)
        date = getTime()[0]
        time = getTime()[1]
        window.addstr(0, maxY - len(date), date)
        window.addstr(1, maxY - len(time), time)
        window.refresh()

        # drawing table labels
        window.addstr(4, 0, "Date\t\tTime\t\tPrice (USD)\t\tStatus")
        window.addstr(5, 0, bar)

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
