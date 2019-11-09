import sqlite3
import xml.etree.ElementTree as ET


def __create_table():
    with sqlite3.connect('account.db') as conn:
        c = conn.cursor()
        sql = """CREATE TABLE IF NOT EXISTS "SecurityInfo" (
        "conid"	INTEGER,
        "assetCategory"	TEXT,
        "currency"	TEXT,
        "description"	TEXT,
        "symbol"	TEXT,
        "underlyingCategory"	TEXT,
        "underlyingSymbol"	TEXT,
        PRIMARY KEY("conid")
        );"""
        c.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS "EquitySummaryByReportDateInBase" (
        "reportDate"	TEXT,
        "accountId"	TEXT,
        "total"	REAL NOT NULL,
        PRIMARY KEY("reportDate","accountId")
        );"""
        c.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS "StatementOfFundsLine" (
        "transactionID"	TEXT,
        "date"	TEXT,
        "reportDate" TEXT,
        "activityDescription"	TEXT,
        "activityCode"	TEXT,
        "amount"	REAL,
        "conid"	INTEGER,
        "currency"	TEXT,
        "tradeCommission"	REAL,
        "tradeID"	INTEGER,
        "tradePrice"	REAL,
        "tradeQuantity"	REAL,
        "tradeTax"	REAL,
        "fxRateToBase" REAL,
        PRIMARY KEY("date","transactionID")
        );"""
        c.execute(sql)
        sql = """CREATE TABLE IF NOT EXISTS "OpenPosition" (
                "conid"	INTEGER,
                "markPrice"	REAL,
                "position" REAL,
                PRIMARY KEY("conid")
                );"""
        c.execute(sql)


def __import_to_db(file):
    with open(file, 'r') as f:
        root = ET.fromstring(f.read())
    with sqlite3.connect('account.db') as conn:
        c = conn.cursor()
        sql = "INSERT OR REPLACE INTO EquitySummaryByReportDateInBase VALUES (?, ?, ?)"
        day_nav_list = [(x.attrib['reportDate'], x.attrib['accountId'], x.attrib['total'])
                        for x in root.iter('EquitySummaryByReportDateInBase')]
        c.executemany(sql, day_nav_list)
        sql = "INSERT OR REPLACE INTO StatementOfFundsLine VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,?, ?, ?)"
        sof_list = [(
            x.attrib['transactionID'],
            x.attrib['date'],
            x.attrib['reportDate'],
            x.attrib['activityDescription'],
            x.attrib['activityCode'],
            x.attrib['amount'],
            x.attrib['conid'],
            x.attrib['currency'],
            x.attrib['tradeCommission'],
            x.attrib['tradeID'],
            x.attrib['tradePrice'],
            x.attrib['tradeQuantity'],
            x.attrib['tradeTax'],
            x.attrib['fxRateToBase']
        ) for x in root.iter('StatementOfFundsLine')]
        c.executemany(sql, sof_list)
        sql = "INSERT OR REPLACE INTO SecurityInfo VALUES (?, ?, ?, ?, ?, ?, ?)"
        sof_list = [(
            x.attrib['conid'],
            x.attrib['assetCategory'],
            x.attrib['currency'],
            x.attrib['description'],
            x.attrib['symbol'],
            x.attrib['underlyingCategory'],
            x.attrib['underlyingSymbol']
        ) for x in root.iter('SecurityInfo')]
        c.executemany(sql, sof_list)
        sql = "DELETE FROM OpenPosition"
        c.execute(sql)
        sql = "INSERT INTO OpenPosition VALUES (?, ?, ?)"
        sof_list = [(
            x.attrib['conid'],
            x.attrib['markPrice'],
            x.attrib['position']
        ) for x in root.iter('OpenPosition')]
        c.executemany(sql, sof_list)


def import_data(filename='data.xml'):
    __create_table()
    __import_to_db(filename)


if __name__ == '__main__':
    import_data('data2015.xml')
    import_data('data2016.xml')
    import_data('data2017.xml')
    import_data('data2018.xml')
    import_data('data2019.xml')
