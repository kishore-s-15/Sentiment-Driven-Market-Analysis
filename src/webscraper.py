# Importing the required libraries

import os
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path
import json
from decouple import config
from langdetect import detect
import time
import sqlite3
import bs4 as bs

from tqdm import tqdm


# Helper function
def delta_date(start_date,end_date):
    return abs((datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days)


class Config:
    def __init__(self):
        """
        Configuration class for financial data extraction.

        Attributes:
        - start_date (str): Start date for data extraction in the format 'YYYY-MM-DD'.
        - end_date (str): End date for data extraction in the format 'YYYY-MM-DD'.
        - tickers (list): List of stock tickers.
        - db_name (str): Name of the database.
        - dir_path (str): Output directory path based on start and end dates.
        - start_date_ (datetime): Start date as a datetime object.
        - end_date_ (datetime): End date as a datetime object.
        - delta_date (int): Number of days between start and end dates.
        """

        self.start_date = "2022-11-26"
        self.end_date = "2023-11-15"
        self.tickers = ['META', 'PLTR', 'COIN', 'DUOL', 'GOOG']

        self.db_name = 'financial_data'
        self.dir_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'output',
            f'{self.start_date}_{self.end_date}/'
        )

        # Create new path if it doesn't exist
        Path(self.dir_path).mkdir(parents=True, exist_ok=True)

        self.start_date_ = datetime.strptime(self.start_date, "%Y-%m-%d")
        self.end_date_ = datetime.strptime(self.end_date, "%Y-%m-%d")

        # Number of days between 2 dates
        self.delta_date = (self.end_date_ - self.start_date_).days

        # Check if start_date is after end_date
        if self.start_date_ > self.end_date_:
            raise ValueError("'start_date' is after 'end_date'")

        # Calculate a date one year ago from the current date
        t = (datetime.now() - relativedelta(years=1))
        d = datetime.strptime(self.start_date, "%Y-%m-%d")


class Scraper:

    def __init__(self, start_date, end_date, start_date_, end_date_, tickers, dir_path, db_name):
        """
        Scraper class for extracting financial news data.

        Parameters:
        - start_date (str): Start date for data extraction in the format 'YYYY-MM-DD'.
        - end_date (str): End date for data extraction in the format 'YYYY-MM-DD'.
        - start_date_ (datetime): Start date as a datetime object.
        - end_date_ (datetime): End date as a datetime object.
        - tickers (list): List of stock tickers.
        - dir_path (str): Output directory path.
        - db_name (str): Name of the database.
        """

        self.max_call = 60
        self.time_sleep = 60
        self.nb_request = 0
        self.finhub_key = config('FINHUB_KEY')
        self.news_header = ['category', 'datetime', 'headline', 'id', 'image', 'related', 'source', 'summary', 'url']
        self.start_date = start_date
        self.end_date = end_date
        self.tickers = tickers
        self.ticker_request = tickers
        self.dir_path = dir_path
        self.db_name = db_name
        self.js_data = []
        self.start_date_ = start_date_
        self.end_date_ = end_date_

    def scrap_data(self):
        """
        Scrap financial news data for the specified tickers and date range.
        """

        for ticker_ in tqdm(self.tickers, desc="Tickers: "):
            self.js_data.clear()
            self.ticker = ticker_ + '_'
            self.ticker_request = ticker_
            self.req_new()
            self.create_table()
            self.clean_table()
            self.lang_review()


    def init_sql(func):
        def wrapper_(self, *args, **kwargs):
            """
            Wrapper function for initializing SQLite connection and cursor.
            """

            conn_ = sqlite3.connect(self.dir_path + self.db_name + '.db')
            c = conn_.cursor()
            func(self, conn_, c, *args, **kwargs)
            conn_.commit()
            conn_.close()

        return wrapper_


    @init_sql
    def clean_table(self, conn_, c):
        """
        Clean the data table by removing NULL entries, NULL values, and duplicate entries.
        """

        c.execute(f"DELETE FROM {self.ticker} WHERE {self.news_header[2]} IS NULL OR "
                  f"trim({self.news_header[2]}) = '';")
        c.execute(f"DELETE FROM {self.ticker} WHERE {self.news_header[1]} IS NULL OR "
                  f"trim({self.news_header[1]}) = '';")
        c.execute(f"DELETE FROM {self.ticker} WHERE rowid NOT IN (SELECT MIN(rowid) "
                  f"FROM {self.ticker} GROUP BY {self.news_header[2]})")


    @init_sql
    def create_table(self, conn_, c):
        """
        Create the data table if it does not exist and add columns.
        """

        c.execute(f'DROP TABLE IF EXISTS {self.ticker}')
        conn_.commit()
        c.execute(f"CREATE TABLE IF NOT EXISTS {self.ticker} ({self.news_header[0]})")
        conn_.commit()

        for header_ in range(len(self.news_header) - 1):
            c.execute(f"ALTER TABLE {self.ticker} ADD COLUMN '{self.news_header[header_ + 1]}'")
            conn_.commit()

        iteration = 0
        for data_ in self.js_data:
            iteration += 1
            try:
                c.execute(f'INSERT INTO {self.ticker} VALUES (?,?,?,?,?,?,?,?,?)',
                          [data_[self.news_header[0]], data_[self.news_header[1]], data_[self.news_header[2]],
                           data_[self.news_header[3]], data_[self.news_header[4]], data_[self.news_header[5]],
                           data_[self.news_header[6]], data_[self.news_header[7]], data_[self.news_header[8]]])
            except:
                print(f"Error at the {iteration}th iteration")

            conn_.commit()


    def iterate_day(func):
        def wrapper_(self, *args, **kwargs):
            """
            Wrapper function for iterating over days and making requests.
            """

            delta_date_ = delta_date(self.start_date, self.end_date)
            date_ = self.start_date
            date_obj = self.start_date_

            for item in tqdm(range(delta_date_ + 1), desc="Days: "):
                self.nb_request += 1
                func(self, date_, *args, **kwargs)
                date_obj = date_obj + relativedelta(days=1)
                date_ = date_obj.strftime("%Y-%m-%d")
                if self.nb_request == (self.max_call - 1):
                    time.sleep(self.time_sleep)
                    self.nb_request = 0

        return wrapper_


    @init_sql
    def lang_review(self, conn_, c):
        """
        Review and delete non-English entries from the data table.
        """

        list_ = []
        c.execute(f"SELECT {self.news_header[2]} FROM {self.ticker}")

        for item_ in c:
            if detect(item_[0]) != 'en':
                list_.append(item_[0])

        query = f"DELETE FROM {self.ticker} WHERE {self.news_header[2]} IN ({','.join(['?'] * len(list_))})"
        c.execute(query, list_)


    @iterate_day
    def req_new(self, date_):
        """
        Make requests to the Finnhub API for financial news data.
        """

        request_ = requests.get(
            'https://finnhub.io/api/v1/company-news?symbol=' + self.ticker_request + '&from=' +
            date_ + '&to=' + date_ + '&token=' + self.finhub_key
        )
        self.js_data += request_.json()


if __name__ == "__main__":
    config = Config()

    scraper = Scraper(
        start_date=config.start_date, end_date=config.end_date,start_date_=config.start_date_,
        end_date_ =config.end_date_, tickers=config.tickers, dir_path =config.dir_path,
        db_name=config.db_name
    )
    scraper.scrape_data()