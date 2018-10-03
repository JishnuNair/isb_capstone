import sqlite3
import requests
import os
import pathlib
from sqlite3 import Error


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


def select_all_10_k(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM idx  WHERE type='10-K' AND substr(date,0,5) != '2015'")

    rows = cur.fetchall()

    for row in rows:
        print(row)
        get_filings(row)

def get_filings(row):
    cik,conm,date = row[0],row[1],row[3]
    year = row[3][:4]
    url = 'https://www.sec.gov/Archives/' + row[4].strip()
    directory = '{0}/{1}'.format(year,cik)
    file_name = '{0}/{1}.xbrl'.format(directory,date)
    if not os.path.exists(directory):
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    with open(file_name,'wb') as fout:
        fout.write(requests.get('%s' % url).content)
        print(url, 'downloaded and wrote to file')


def main():
    database = "/home/jishnu/Documents/ISB/Term3/capstone/repo/filings/edgar_idx.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        # print("Testing query")
        select_all_10_k(conn)

if __name__ == '__main__':
    main()
