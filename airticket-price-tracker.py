#!usr/bin/env python

from __future__ import print_function, unicode_literals

import datetime
import json
import random
import re
import sys
import smtplib
import time
import sqlite3

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

if (sys.version_info > (3, 0)):
    raw_input = input
    unicode = str

base_url = "https://booking.airasia.com/Flight/Select?o1={}&d1={}&culture=en-GB&dd1={}&ADT=1&CHD=0&inl=0&s=true&mon=true&cc=INR&c=false"
current_latest = ""
global latest_fare

def getSoup(_url):
    """
    Returns the html-parsed-BeautifulSoup object for the given URL.

    Parameters:
        _url: String: the http(s) link to get html from
    """

    try:
        r = requests.get(_url)
    except Exception as e:
        print(e)
        sys.exit("\n CONNECTION ERROR: Check your Internet connection again.\n")

    return BeautifulSoup(r.text, 'html.parser')

def getPrice(_string):
    return float(re.sub(r'[^\d.]+','', _string))

def getLatestFare(_origin, _destination, _date):
    """
    _origin and _destination take airport codes , e.g. BLR for Bangalore
    _date in format YYYY-MM-DD e.g.2016-10-30
    Returns either:
        10 latest results from the results page.
        1 lastest result from the results page.
    """
    try:
        _url = base_url.format(_origin, _destination, _date)
        soup = getSoup(_url)
        fare_list = soup.find('ul').find_all('li',{"class":["active","not-active"]})
        fares = []
        for fare in fare_list:
            fares.append({'price':getPrice(fare.find('a').find('div').findChildren()[2].string),'date':fare.find('a').find('div').findChildren()[0].string})
    except Exception:
        sys.exit("No Route found.")
    return fares

def initDb():
    conn = sqlite3.connect('atpt.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    a = c.fetchone()
    if a and 'airasia' in a:
        return c,conn
    else:
        c.execute('''CREATE TABLE airasia(date text,tminus3 real , tminus2 real, tminus1 text, t real, tplus1 real, tplus2 real, tplus3 real)''')
        conn.commit()
        return c,conn

def areSame(last_fare, latest_fare):
    for i in range(0,len(last_fare)):
        if float(last_fare[i]) != float(latest_fare[i]['price']):
            return False
    return True

def checkUpdate(origin, destination, date):
    """
    Returns True if result updated. False otherwise.
    """
    c,conn = initDb()
    c.execute('SELECT max(ROWID) FROM airasia')
    max_id = c.fetchone()
    latest_fare = getLatestFare(origin,destination,date)
    last_fare = None
    if(None not in max_id):
        c.execute('SELECT * FROM airasia WHERE ROWID=?', max_id)
        last_fare = c.fetchone()[1:]
        if areSame(last_fare, latest_fare):
            return False, last_fare, latest_fare
    latest_fare_list = [str(datetime.datetime.now())]
    for fare in latest_fare:
        latest_fare_list.append(fare['price'])
    update_query = 'INSERT INTO airasia VALUES ("{}",{},{},{},{},{},{},{})'.format(*latest_fare_list)
    c.execute(update_query)
    conn.commit()
    conn.close()
    return True, last_fare, latest_fare


def sendMail(latest_fare, last_fare, origin, destination, date):
    """
    Sends email to the recepients with the _content
    """
    fares = []
    for i in range(0, len(latest_fare)):
        fares.append(latest_fare[i]['date'])
        if(last_fare is None):
            fares.append("  -")
        else:
            fares.append(last_fare[i])
        fares.append(latest_fare[i]['price'])
    fares.extend([origin, destination, date])
    result = """\
    <html>
    <body>
    <h3>AirAsia ticket price Change</h3>
    <table>
      <tr>
        <th>Date</th>
        <th>Previous Fare</th>
        <th>Current Fare</th>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>
    </table>
    <hr>
    <p><a href="https://booking.airasia.com/Flight/Select?s=True&o1={}&d1={}&ADT=1&dd1={}&mon=true&&c=false">AirAsia</a></p>
    <p><a href="https://sharad5.github.io/">( ͡° ͜ʖ ͡°)</a></p>
    </body>
    </html>
    """.format(*fares)

    from_addr = "SENDER_EMAIL"
    to_addr = ["RECEIVER_EMAIL","RECEIVER_EMAIL"]
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addr)
    msg['Subject'] = "Price Change Alert"
    msg.attach(MIMEText(result, 'html'))

    # print(result)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_addr, "PASSWORD")
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()
    print("{} - Mail sent to {} people.".format(datetime.datetime.now(), len(to_addr)))

def isCodeValid(code):
    valid_codes = ['IXA', 'AGR', 'AMD', 'IXD', 'ATQ', 'IXU', 'IXB', 'BLR', 'BHU', 'BHO', 'BBI',
                    'BHJ', 'CCU', 'IXC', 'MAA', 'COK', 'CJB', 'NMB', 'DED', 'DIB', 'DMU', 'DIU',
                    'GAU', 'GOI', 'GWL', 'HBX', 'HYD', 'IMF', 'IDR', 'JAI', 'IXJ', 'JGA', 'IXW',
                    'JDH', 'JRH', 'KNU', 'HJR', 'CCJ', 'IXL', 'LKO', 'LUH', 'IXM', 'IXE', 'BOM',
                    'NAG', 'NDC', 'ISK', 'DEL', 'PAT', 'PNY', 'PNQ', 'PBD', 'IXZ', 'PUT', 'BEK',
                    'RAJ', 'IXR', 'SHL', 'IXS', 'SXR', 'STV', 'TEZ', 'TRZ', 'TIR', 'TRV', 'UDR',
                    'BDQ', 'VNS', 'VGA', 'VTZ']
    return code in valid_codes

def isDateValid(date):
    reg = r'^(201[6-7])-(0[1-9]|1[0-2])-([0-2][0-9]|3[0-1])$'
    return re.match(reg, date) is not None

def getOrigin():
    while True:
        origin = raw_input("Enter the airport code of origin city (e.g. DEL) :")
        if isCodeValid(origin):
            return origin

def getDestination():
    while True:
        destination = raw_input("Enter the airport code of destination city (e.g. BLR) :")
        if isCodeValid(destination):
            return destination

def getDate():
    while True:
        date = raw_input("Enter the date of intended travel in YYYY-MM-DD format :")
        if isDateValid(date):
            return date

def main(is_first):
    global origin, destination, date
    if is_first:
        origin = getOrigin()
        destination = getDestination()
        date = getDate()
    update = checkUpdate(origin, destination, date)
    if update[0]:
        last_fare = update[1]
        latest_fare = update[2]
        sendMail(latest_fare, last_fare, origin, destination, date)
    else:
        print("%s No Price change detected."%str(datetime.datetime.now()))
    pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            wait_seconds = int(sys.argv[1])
        except ValueError:
            sys.exit("Enter waiting time in seconds. Eg.: 300")
        is_first = True
        while True:
            main(is_first)
            is_first = False
            time.sleep(wait_seconds)
    main()
