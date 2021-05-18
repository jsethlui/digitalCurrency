
# link: https://jamesgeorgedunn.com/2020/10/05/using-python-and-pandas-to-analyse-cryptocurrencies-with-coinapi/

import requests
import sys
import os
import time
import smtplib
from signal import signal, SIGINT
from smtplib import SMTPResponseException
from email.message import EmailMessage
from datetime import datetime
from pprint import pprint

apiAccessCount = 0

class Color:
    FAIL    = '\033[91m'    # red
    SUCCESS = '\033[92m'    # green
    BOLD    = '\033[1m'     # bold
    END     = '\033[0m'     # end

def signalHandler(sig, frame):
    message  = "\nKeyboardInterrupt"
    message += "\nExiting..."
    print(message)
    sys.exit(1)

def getCryptoCurrencyPrice(cryptoBase):
    url = "https://rest.coinapi.io/v1/exchangerate/" + str(cryptoBase) + "/USD"
    apiKey = "F630E2F0-8BBC-4DDF-AE7B-41E2F54B97D2"
    header = {"X-CoinAPI-Key": apiKey}
    response = requests.get(url, headers = header)
    responseJson = response.json()

    statusCode = response.status_code
    message = ""
    if (statusCode == 429):   # too many requests
        sys.stderr.write(Color.FAIL + "Error: " + Color.END + "max requests exceeded (status code = " + str(statusCode) + ")\n")
        sys.exit(1)

    return responseJson

def messagePhoneNumber(subject, to, body):
    message = EmailMessage()
    message["subject"] = subject
    message["to"] = to
    message.set_content(body)

    user = ""
    password = ""
    message["from"] = user

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to, "test message")
        server.quit()
    except SMTPResponseException as error:
        errorCode = error.smtp_code
        errorMessage = error.smtp_error
        sys.stderr.write(Color.FAIL + "Error: " + Color.END + str(errorMessage) + " (error code = " + str(errorCode) + ")\n")
        sys.exit(1)

def main(argv):

    os.chdir(sys.path[0])             # to locate file
    signal(SIGINT, signalHandler)     # registering interrupt signal handler

    '''
        DOGE ==  Dogecoin
        ETH  ==  Ethereum
        BTC  ==  Bitcoin
        LTC  == Litecoin
    '''
    rateMapping = {"DOGE": "Dogecoin", "ETH": "Ethereum", "BTC": "Bitcoin", "LTC": "Litecoin"}
    try:
        idBase = sys.argv[1]                # id base
        cyptoPriceThreshold = sys.argv[2]   # cents
    except IndexError:          # when no argument specified
        message  = Color.FAIL + "Error: " + Color.END + "invalid cryptocurrency base specified\n"
        message += Color.FAIL + "Valid Bases: " + Color.END
        for base in rateMapping.values():
            message += str(base) + "   "
        sys.stderr.write(message + "\n")
        sys.exit(1)

    # getting number of times program has accessed crpyto (max is 100)
    f = open("log.txt", "r")
    line = f.readline()
    f.close()

    if (line == ""):
        apiAccessCount = 0
    else:
        apiAccessCount = int(line)

    if (apiAccessCount >= 100):
        f = open("log.txt", "w")
        f.write(0)                  # reset count to 0
        f.close()
        apiAccessCount = "error"

    labels  = Color.BOLD + "\nRate: " + Color.END + str(rateMapping[str(idBase)]) + " (" + str(idBase) + ")\t\t"
    labels += Color.BOLD + "Threshold (¢): " + Color.END + str(cyptoPriceThreshold) + "\t"
    labels += Color.BOLD + "API Access Count: " + Color.END + str(apiAccessCount) + "\n"
    labels += Color.BOLD + "Date" + Color.END + "\t\t"
    labels += Color.BOLD + "Time" + Color.END + "\t\t"
    labels += Color.BOLD + "Price (USD)" + Color.END + "\t\t"
    labels += Color.BOLD + "Status" + Color.END + "\t"
    print(labels)
    for i in range(76):
        print("-", end = "")
    print("\n")

    messagePhoneNumber("Test Subject",
                        "4156029495@txt.att.net",
                        "Test Body")

    print(getCryptoCurrencyPrice(idBase))

    while (True):
        currentRate = getCryptoCurrencyPrice(idBase)["rate"]
        apiAccessCount += 1

        message  = datetime.now().strftime("%d/%m/%Y\t%H:%M:%S")
        message += "\t" + str(currentRate) + "\t"
        if (foundNewMax == True):
            message += " NEW "
        else:
            message += "  -  "
        print(message)

        # logging api access count
        f = open("log.txt", "w")
        f.write(str(apiAccessCount))
        f.close()

#        time.sleep(840)     # 14 minutes
        time.sleep(3)

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
