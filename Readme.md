### Welcome to the Crypto Trader program


### Introduction

This project will help you scrape data from Coimarketcap.com, a website that provides information regarding the crypotcurrency markets.
The code allows you to scrape information regarding the top 10 cryptocurrencies (by market capitalization) and then provides a table to
help you find the cheapest exchanges to buy these cryptocurrencies (tailored specifically for those who are in US), thus performing
market arbitrage.

### Part I - Getting Started - Downloading necessary files
- Download the following files from this Github repository into the same folder on your desktop:
  - SI507F17_finalproject.py - this is the actual program
  - SI507F17_finalproject_tests.py - this provides to test to ensure the code is running properly
  - config.py - this is information for setting up your database
  - requirements.txt - this contains the necessary packages used for the code. You will need to install these packages for the code to work.
  - plotlyconfig.py - this makes sure that the Plotly visualizations work

### Part II - Getting Started - Running the code
- We will be using Python3 for this project
- Pip install everything from the requirements.txt file
- Create a database on the terminal, the name of the database is in the config.py file
- On your terminal, to run the program, type, "python3 SI507F17_finalproject.py"

### Part III - What output to expect
- Once you run the code, you will notice that a web browser opens as the program is scraping two pages on coinmarketcap.com
  to get information about the top 10 crypotcurrencies and their respective exchanges. It will fetch a fresh copy first_row
  and then only fetch a fresh copy every 10 minutes. Up-to-date information is important for prices so that is why the cache
  expiry is quite short.
- Two tabs will open. These will bring you to one Plotly chart and another Plotly table. You can see an example screenshot of both
  of these in this Githbu repository ('Crypto Chart' and 'Crypto Arbitrage Table'). If you aren't logged in you can either login or
  click "x" to simply see the chart and table.
- Crypto Chart shows you a bar chart of the top 10 crytpocurrencies with their respective prices. The left most coin is the largest
  cryptocurrency (by market cap)
- Crypto Arbitrage Table will show you a table of these top 10 cryptocurrencies, organized by the respective markets where you are able
  to sell and buy them. This table is ranked by most valuable coin first (by market cap) and shows the lowest price at which to buy this
  and subsequent coins. This allows for potential market arbitrage as you can buy a coin at the lowest price listed and then sell it
  at the higher price listed further down the chart. For instance, as you can see in the screenshot, you can buy Bitcoin on the WEX
  exchange for $15,210 and then sell it on CEX.IO for $17,137.50.

### Part IV - Resources used
- I received assistance from Anand Doshi, a Graduate Student Instructor at the University of Michigan, with this project.
  In particular, he helped with the usage of Selenium and Webdriver, two packages that allowed me to scrape information from
  portions of coinmarketcap.com that were coded in Javascript
- This code also re-uses code from previous projects in UMSI's SI 507 course specifically the code to cache data and to set up
  a PSQL database.
