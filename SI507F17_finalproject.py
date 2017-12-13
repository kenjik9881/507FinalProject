from bs4 import BeautifulSoup as Soup
from datetime import datetime
# from urllib2 import urlopen
import unittest
import requests
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import psycopg2
import psycopg2.extras
from config import *

import plotly
import plotlyconfig
import plotly.plotly as py
import plotly.graph_objs as go

##Add to readme used selenium and chromewebdriver

#---FIGURE OUT HOW TO CACHE TO EXPIRE AFTER 1 HOUR-------!

# #Scraping with BeautifulSoup--original cache file

# try:
#   coinmarketcap_main_data = open("main_page.html",'r').read()
# except:
#   coinmarketcap_main_data = requests.get("https://coinmarketcap.com/").text
#   f = open("main_page.html",'w')
#   f.write(coinmarketcap_main_data)
#   f.close()

# -----------------------------------------------------------------------------
# Constants, Global variables
# -----------------------------------------------------------------------------
CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
chrome_browser = None

# -----------------------------------------------------------------------------
# Load cache file
# -----------------------------------------------------------------------------
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}


# -----------------------------------------------------------------------------
# Cache functions
# -----------------------------------------------------------------------------
def has_cache_expired(timestamp_str, expire_in_seconds):
    """Check if cache timestamp is over expire_in_seconds old""" #docstring
    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_seconds = delta.seconds

    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_seconds < expire_in_seconds:
        return False
    else:
        return True
#returns false or true

def get_from_cache(url):
    """If URL exists in cache and has not expired, return the html, else return None"""
    if url in CACHE_DICTION:
        url_dict = CACHE_DICTION[url]

        if has_cache_expired(url_dict['timestamp'], url_dict['expire_in_seconds']):
            # also remove old copy from cache
            del CACHE_DICTION[url]
            html = None
        else:
            html = CACHE_DICTION[url]['html']
    else:
        html = None

    return html


def set_in_cache(url, html, expire_in_seconds):
    """Add URL and html to the cache dictionary, and save the whole dictionary to a file as json"""
    CACHE_DICTION[url] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_seconds': expire_in_seconds
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)


def get_html_from_url(url, expire_in_seconds=600, use_chromedriver=False, wait_for_id=None): #will try to look for url in the cache
    """Check in cache, if not found, load html, save in cache and then return that html"""
    global chrome_browser
    # check in cache
    html = get_from_cache(url)
    if html:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
            print()
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(url))
            print()

        # fetch fresh
        if use_chromedriver:
            if not chrome_browser:
                chrome_browser = webdriver.Chrome()
            chrome_browser.get(url)
            delay = 3 # seconds
            try:
                myElem = WebDriverWait(chrome_browser, delay).until(EC.presence_of_element_located((By.ID, wait_for_id)))
                print("Page is ready!")
            except TimeoutException:
                print("Loading took too much time!")

            html = chrome_browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string

        else:
            response = requests.get(url)

            # this prevented encoding artifacts like
            # "Trumpâs Tough Talk" that should have been "Trump's Tough Talk"
            response.encoding = 'utf-8'

            html = response.text

        # cache it
        set_in_cache(url, html, expire_in_seconds)

    return html
#-----------------------------------------------------end of caching caching (This code references code from nytimes.py)

#----Part I- Scrape the Homepage--------

latest_coin_html = get_html_from_url("https://coinmarketcap.com/", expire_in_seconds=60)

coin_soup = Soup(latest_coin_html, 'html.parser')
coin_table = coin_soup.find_all("tr") #finding the rows in the table

open_list = []
for first_row in coin_table[1:11]:
    row = {}
    coin_rank = first_row.find("td", {"class": "text-center"}).text.strip() #this gives the ranking of the coin
    coin_name = first_row.find("a", {"class": "currency-name-container"}).text.strip() #this gives the  name of the coin
    coin_price = first_row.find("a", {"class": "price"}).text.strip() #this gives the price of the coin
    coin_marketcap = first_row.find("td", {"class": "no-wrap market-cap text-right"}).text.strip() #this gives market cap of coin
    coin_supply_line = first_row.find("td", {"class":"no-wrap text-right circulating-supply"})
    coin_supply = coin_supply_line.find("span", {"data-supply-container": ""}).text.strip() #this gives the supply of the coin
    coin_24hrchange = first_row.find("td", {"class": "percent-24h"}).text.strip() #this gives percent change over 24 hours
    row['coin_rank'] = coin_rank
    row['coin_name'] = coin_name
    row['coin_price'] = coin_price
    row['coin_marketcap'] = coin_marketcap
    row['coin_supply'] = coin_supply
    row['coin_24hrchange'] = coin_24hrchange

    open_list.append(row)


class Cryptocurrency(object):
    """ A class to represent one cryptocoin, from data received from Coin Marketcap homepage. """

    def __init__(self, crypto_dictionary):
        self.coin_rank = int(crypto_dictionary['coin_rank'])
        self.name = crypto_dictionary['coin_name']
        self.price_string = crypto_dictionary['coin_price'].replace(",", "")
        self.price = round(float(self.price_string[1:]), 2)
        self.marketcap_string = crypto_dictionary['coin_marketcap'].replace(",", "")
        self.marketcap = int(self.marketcap_string[1:])
        self.supply = crypto_dictionary['coin_supply']
        self.percent_change_string = crypto_dictionary['coin_24hrchange']
        self.percent_change = round(float(self.percent_change_string[:-1]),2)

    def __getitem__(self, key):
        if key == "coin_rank":
            return self.coin_rank
        if key == "name":
            return self.name
        if key == "price":
            return self.price
        if key == "marketcap":
            return self.marketcap
        if key == "supply":
            return self.supply
        if key == "percent_change":
            return self.percent_change

    def __str__(self):
        return "{name},{coin_rank},{price}, {marketcap}, {supply}, {percent_change}".format_map(self)
        #return "{name},{coin_rank},{price}, {marketcap}, {supply}, {percent_change}".format(self.name, self.coin_rank, self.price, self.marketcap, self.supply, self.percent_change)
        #return "{} | {}".format(self.name, self.price)

    def __contains__(self, astring):
        return astring in self.name

    def __repr__(self):
        return "Name = {} | Price = {:0.2f} | Percentage Change = {}".format(self.name, self.price, self.percent_change)

    def get_old_price(self): #this gets the old price from 24 hours ago, returns an integer
        if self.percent_change > 0:
            self.old_price = self.price / (1 + (self.percent_change/100))
        else:
            self.old_price = self.price / (1 + (self.percent_change/100))
        return round(self.old_price,2)



coin_instances = [] #passing through the class, this has instance of top 10 crypots

for coin in open_list:
    coin_instance = Cryptocurrency(coin)
    coin_instances.append(coin_instance)

print(coin_instances[0])

# coin_instances = [Cryptocurrency(x) for x in open_list] #list comprehension of the above four lines


print("----------------NEW RUNNING----------")
# for coin in coin_instances:
#     print(repr(coin))

# for coin in coin_instances:
#     print("Bit" in coin)


#------Part 2: Scraping the Markets page to find the best market data------#
#this function return the markets for any given currency
def get_us_markets_for(currency):
    # currency = 'bitcoin'
    bitmarket_html = get_html_from_url("https://coinmarketcap.com/currencies/{0}/#markets".format(currency),
        expire_in_seconds=6000, use_chromedriver=True, wait_for_id='markets-table')


    bitmarket_soup = Soup(bitmarket_html, 'html.parser')
    bitmarket_table = bitmarket_soup.find("tbody")

    all_markets = bitmarket_table.find_all("tr", {"role":"row"})

    bitmarket_list = [] #now have a list of dictionaries

    #lets get the name of the coin this market is for
    # intial_coin_name = bitmarket_soup.find("h2", {"class": "pull-left"}).text.strip()
    # coin_name = intial_coin_name.replace("Markets", "").strip()

    def get_coin_name():
        exchange_coin_name = bitmarket_soup.find("h1", {"class":"text-large"}).img.get('alt').strip() #grab the name of the coin
        return exchange_coin_name

    for one_row in all_markets: #gets all exchanges
        row = {}
        exchange_name = one_row.find("a").text.strip() #grabs exchange name
        exchange_price = one_row.find("span", {"class":"price"}).text.strip() #grabs price of the coin on this exchange
        exchange_pair = one_row.find("a", {"target":"_blank"}).text.strip()
        row['exchange_name'] = exchange_name
        row['exchange_price'] = exchange_price
        row['exchange_pair'] = exchange_pair
        bitmarket_list.append(row)

    #This bitmarket_list has duplicates, we want to filter by exchange_pair that serves US customers
    #also add in the name of the coin served
    US_exchanges_list = []
    for exchange in bitmarket_list:
        name_of_coin = get_coin_name()
        exchange['Name of coin'] = name_of_coin

    for exchange in bitmarket_list:
        exchange_pair = exchange['exchange_pair'].split("/")
        if exchange_pair[1]== 'USD':
            US_exchanges_list.append(exchange)

    return US_exchanges_list

# for each_coin in coin_instances:
#     get_us_markets_for(each_coin

top10_coins = []
for each_coin in coin_instances:
    top10_coins.append(each_coin.name)

top10_coins_hyphenated = [] #this now has a names that can pass through the function
for each_coin in top10_coins:
    top10_coins_hyphenated.append(each_coin.replace(" ", "-"))

markets_for_top10 = [] #this is a list of dictionaries

for each_coin in top10_coins_hyphenated: #this runs every coin from the top 10 in function
    one_coin_markets = get_us_markets_for(each_coin)
    markets_for_top10.extend(one_coin_markets) #extend flattens a list by putting in another list

print(json.dumps(markets_for_top10, indent=2)) #this pretty prints, dictionaries



class Exchange(object): #passes through a dictionary of Crypto Markets from the def get_us_markets_for(currency) function
    """ A class to represent one Exchange, from data received from Coin Marketcap's Bitcoin Markets. """
    def __init__(self, market_dictionary):
        self.exchange_name = market_dictionary['exchange_name']
        self.exchange_price_string = market_dictionary['exchange_price'].replace(",", "")
        self.exchange_price = round(float(self.exchange_price_string[1:]), 2)
        self.name_of_coin = market_dictionary['Name of coin']

    def __getitem__(self, key):
        if key == "exchange_name":
            return self.exchange_name
        if key == "exchange_price":
            return self.exchange_price
        if key == "name_of_coin":
            return self.name_of_coin

    def __str__(self):
        return "This market named {}, sells {} at a price of {:0.2f}".format(self.exchange_name, self.name_of_coin, self.exchange_price)

exchange_instance_list = [] #This is a list of instances of exchanges that serve the US for all coins


for exchange_dict in markets_for_top10:
    exchange_instance = Exchange(exchange_dict)
    exchange_instance_list.append(exchange_instance)

#----------------By this point in the code
# First part of code gives the top 10 cryptos in the "coin_instances" list
# Second part of the code gives markets for any crypto that gets run through that function, it puts the exchanges for the top 10 cryptos into the exchange_instance_list


#------Part 3: Part 3: Creating and using Databases-------

#----this is one way to setup database-----

db_connection, db_cursor = None, None

def get_connection_and_cursor():
    global db_connection, db_cursor
    if not db_connection:
        try:
            if db_password != "":
                db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
                print("Success connecting to database")
            else:
                db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
        except:
            print("Unable to connect to the database. Check server and credentials.")
            sys.exit(1) # Stop running program if there's no db connection.

    if not db_cursor:
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

db_connection, db_cursor = get_connection_and_cursor()

def setup_database():
    # Involves DDL commands
    # DDL --> Data Definition Language
    # CREATE, DROP, ALTER, RENAME, TRUNCATE

    # conn, cur = get_connection_and_cursor()
    db_cursor.execute("DROP TABLE IF EXISTS Coins")
    db_cursor.execute("DROP TABLE IF EXISTS Exchanges")

    db_cursor.execute("CREATE TABLE Coins(name VARCHAR(128) PRIMARY KEY,  coin_rank INTEGER, price DOUBLE PRECISION, marketcap BIGINT, supply VARCHAR(128), percent_change DOUBLE PRECISION)")

    #Create Exchanges--does name_of_coin have to reference here?
    db_cursor.execute("CREATE TABLE Exchanges(ID SERIAL PRIMARY KEY, exchange_name VARCHAR(128), name_of_coin VARCHAR(128),  exchange_price DOUBLE PRECISION)")

    db_connection.commit()
    print('Setup database complete')

setup_database()

#inserting in coin & exchange data into two database tables----

for coin in coin_instances:
    db_cursor.execute("""INSERT INTO Coins(name,coin_rank,price, marketcap, supply, percent_change) VALUES (%(name)s, %(coin_rank)s, %(price)s, %(marketcap)s, %(supply)s, %(percent_change)s)  """, coin)

for exchange in exchange_instance_list:
    db_cursor.execute("""INSERT INTO Exchanges(exchange_name, name_of_coin, exchange_price) VALUES (%(exchange_name)s, %(name_of_coin)s, %(exchange_price)s)  """, exchange)

print("Query the Coin tables to pull the average price of the coins on all the exchanges and order them by their rank")
db_cursor.execute(""" SELECT "coins"."coin_rank", "coins"."name", "coins"."marketcap", "coins"."price" FROM "coins" ORDER BY "coins"."coin_rank" ASC """)
average_coin_prices = db_cursor.fetchall()
# print(json.dumps(average_coin_prices, indent=2))

print("Query the two tables to pull the price of the coins on all the exchanges and order them in ascending order")
db_cursor.execute("""SELECT "exchanges"."name_of_coin", "exchanges"."exchange_name", "exchanges"."exchange_price" FROM "exchanges" INNER JOIN "coins" ON ("exchanges"."name_of_coin") = ("coins"."name") ORDER BY "exchanges"."name_of_coin" DESC, "exchanges"."exchange_price" ASC """)
market_prices = db_cursor.fetchall()
# print(json.dumps(market_prices, indent=2))

#--------------PART 4 VISUALIZE WITH PLOTLY---------------#
#GOALS:
# A scatter plot of the coins, average price for the top 10 on a plot
# A scatter plot of the exchanges for all coins, with a logo for each coin or color code for each coin on that scatter plot
#use .keys and .values to unpack diciontary to list
plotly.tools.set_credentials_file(username=plotlyconfig.username, api_key=plotlyconfig.api_key)

coin_values = []
for coin in average_coin_prices:
    coin_values.append([coin['name'], coin['price']])
# print(coin_values)

coin_names = []
for coin in coin_values:
    coin_names.append(coin[0])
# print(coin_names)

coin_prices = []
for coin in coin_values:
    coin_prices.append(coin[1])
# print(coin_prices)

data = [go.Bar(
            x=coin_names,
            y=coin_prices
    )]
py.plot(data, filename='basic-bar')

exchange_values = []
for exchange in market_prices:
    exchange_values.append([exchange['name_of_coin'], exchange['exchange_name'], exchange['exchange_price']])

exchange_coin_names = []
for coin_type in exchange_values:
    exchange_coin_names.append(coin_type[0])
# print(exchange_coin_names)

exchange_names = []
for name in exchange_values:
    exchange_names.append(name[1])
# print(exchange_names)

exchange_prices = []
for price in exchange_values:
    exchange_prices.append(price[2])
# print(exchange_prices)

trace = go.Table(
    header=dict(values=['Name of Coin', 'Exchange', 'Exchange Price']),
    cells=dict(values=[exchange_coin_names,
                       exchange_names, exchange_prices]))

data = [trace]
py.plot(data, filename = 'basic_table')

if chrome_browser:
    chrome_browser.close()
