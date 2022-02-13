from abc import abstractmethod
import sqlite3
import json
import requests
import time
import requests
import datetime as datetime
import pandas as pd

# connection
conn = sqlite3.connect("news.db")  # 1 STEP

# cursor
c = conn.cursor()

# BASE TIME
base = datetime.datetime.today()
rangedays = (base-datetime.datetime(1852, 1, 1, 0, 0, 0)).days

# making a list of the past 12 months
months = [(base - datetime.timedelta(days=x)).month for x in range(rangedays)]
# making a list of years for each month
years = [(base - datetime.timedelta(days=x)).year for x in range(rangedays)]

# creating the list of pairs (year, month)
dates = list(dict.fromkeys(zip(years, months)))


# create table
c.execute("""CREATE TABLE IF NOT EXISTS news (
        headline TEXT,
        subsection TEXT,
        date DATE
    )""")

conn.commit()


def nyt_articles(dates):
    """
    This function retreive the articles data give a list of tuples (year, months).
    Each article will have the following structure: headline, abstract, document_type, type_of_material, keywords, news desk, section name, subsection name, word count, date.

    Args:
        dates (list): list of tuples containing (year, months)

    Returns:
        dict: A dictionary containing the articles informations
    """

    for date in dates:
        response = requests.get(
            f"https://api.nytimes.com/svc/archive/v1/{date[0]}/{date[1]}.json?api-key=nAI3eDl8Go6oj8eEi06R84NLgIHDBo9D")

        data = json.loads(response.text)

        for article in data["response"]["docs"]:

            # appending headline
            headline = article["headline"]["main"]

            # appending subsection name
            # some articles don't have subsection name, we will use nan instead
            try:
                subsection = article["subsection_name"]
            except:
                subsection = None

            # appending date
            date = article["pub_date"]

            c.execute(
                "INSERT INTO news VALUES (?, ?, ?)",
                (headline, subsection, date))

        time.sleep(6)  # to avoid hitting per minute rate limit
        print(c.lastrowid)


nyt_articles(dates)
conn.commit()
# c.execute('SELECT * FROM news')

# print(c.fetchall())

# query = '''
# SELECT *
# FROM news
# '''

# df = pd.read_sql(query, conn,
#                  parse_dates=["date"])
# print(df)

conn.close()  # CLOSE conn
