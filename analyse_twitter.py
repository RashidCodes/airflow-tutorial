#!/usr/bin/env python

import os
import os.path
import re
from datetime import datetime
import mysql.connector as mysql
import pandas as pd



def connect_db():
	
    """Connect to a given database

    Returns:
        dbconnect: MySQL database connection object

    """

    DATABASE = {
        "host": "localhost",
        "user": "airflow",
        "password": "python2019",
        "db": "airflowdb"
    }


    try:
        dbconnect = mysql.connect(
            host = DATABASE.get("host"),
            user = DATABASE.get("user"),
            password = DATABASE.get("password"),
            db = DATABASE.get("db")
        )

        print("connected")
        return dbconnect
    
    except mysql.Error as e:
        print(e) 

# ----------------------------------------------
#  Database related functions
# ----------------------------------------------


def sql_to_csv(my_database, my_table):

    dbconnect = connect_db()

    cursor = dbconnect.cursor()

    query = f"SELECT * FROM {table}"
    all_tweets = pd.read_sql(query, dbconnect)

    if os.path.exists("./data"):
        all_tweets.to_csv("./data/raw_tweets.csv", index=False)

    else:
        os.mkdir("./data")
        all_tweets.to_csv("./data/raw_tweets.csv", index=False)


def sql_to_df(my_table):
    dbconnect = connect_db()

    cursor = dbconnect.cursor()

    query = f"SELECT * FROM {my_table}"

    # store in data frame

    df = pd.read_sql(query, dbconnect, index_col="id")

    cursor.close()
    dbconnect.close()

    return df


# ----------------------------------------------
#  Data processing
# ----------------------------------------------


def clean_data(df):

    # Make all usernames lowercase
    clean_df = df.copy()
    clean_df["user"] = df["user"].str.lower()

    # keep only non RT
    clean_df = clean_df[clean_df["tweet"].str.contains("a")]

    return clean_df


def save_df(df):
    today = datetime.today().strftime("%Y-%m-%d")

    if os.path.exists("./data"):
        df.to_csv(f"./data/{today}-clean-df.csv", index=None)

    else:
        os.mkdir("./data")
        df.to_csv(f"./data/{today}-clean-df.csv", index=None)


if __name__ == "__main__":

    df = sql_to_df("tbl_tweets")
    print("Database loaded in df")

    clean_df = clean_data(df)

    save_df(clean_df)
