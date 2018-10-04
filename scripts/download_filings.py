import sqlite3
import requests
import os
import re
import pathlib
import pandas as pd
from sqlite3 import Error

def get_ciks(companies_file):
    df = pd.read_csv(companies_file)
    tickers = list(df['Ticker'])
    URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
    CIK_RE = re.compile(r'.*CIK=(\d{10}).*')

    cik_dict = {}
    ciks = []
    for ticker in tickers:
        f = requests.get(URL.format(ticker), stream = True)
        results = CIK_RE.findall(f.text)
        if len(results):
            cik_dict[str(int(results[0]))] = str(ticker).lower()
            ciks.append(str(int(results[0])))

    return ciks,cik_dict


def create_connection(db_file):
    """ create a database connection to the SQLite database specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def select_all_10_k(conn,ciks):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM idx  WHERE type='10-K' AND cik IN ({0})".format(",".join(ciks)))
    rows = cur.fetchall()
    return rows


def get_filings(row,cik_dict,WORK_DIR):
    cik,conm,date = row[0],row[1],row[3]
    ticker = cik_dict[cik]
    year = row[3][:4]
    url = 'https://www.sec.gov/Archives/' + row[4].strip()
    directory = '{0}/{1}/{2}'.format(WORK_DIR,year,ticker)
    file_name = '{0}/{1}.xbrl'.format(directory,date)
    if not os.path.exists(directory):
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open(file_name,'wb') as fout:
        fout.write(requests.get('%s' % url).content)
        print(url, 'downloaded and wrote to file')


def main():
    WORK_DIR = '/home/jishnu/Documents/ISB/Term3/capstone/repo/isb_capstone-master/repo'
    database = "{0}/edgar_idx.db".format(WORK_DIR)
    companies_file = "{0}/companies.csv".format(WORK_DIR)

    ciks,cik_dict = get_ciks(companies_file)

    # create a database connection
    conn = create_connection(database)
    with conn:
        rows = select_all_10_k(conn,ciks)

    for row in rows:
        print(row)
        get_filings(row,cik_dict,WORK_DIR)

if __name__ == '__main__':
    main()
