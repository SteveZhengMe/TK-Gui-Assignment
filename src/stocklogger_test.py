# This is the testcases

import unittest
import sqlite3
from sqlite3 import Error
import os
import stock_logger as app

class StockLogUnitTest(unittest.TestCase):
    db = "stocklog_unittest.db"

    # Delete the testing DB and recreate a new one when starting testing
    def setUp(self):
        if os.path.exists(self.db):
            os.remove(self.db)
        try:
            dataController = app.DataController(self.db)
        except:
            print("="*10 + "Test Initialization Fail" + "="*10)
        else:
            pass

    # If the database and testing data can be rebuild
    def test_DBInitialize(self):
        try:
            conn = sqlite3.connect(self.db)
            result = conn.execute("select count(1) from stocks")
            self.assertEqual(result.fetchone()[0],10)
        finally:
            if conn:
                conn.close()

    # If the summary information based on the testing data is correct
    def test_getSummaryInfo(self):
        dataController = app.DataController(self.db)
        dataResults = dataController.getSummaryInfo()
        self.assertEqual(len(dataResults), 6)

        tradeSymbols = dataResults[0]
        self.assertEqual(len(tradeSymbols),2)
        self.assertIn(('AAPL',),tradeSymbols)
        self.assertIn(('MSFT',),tradeSymbols)

        OldestTrade = dataResults[1]
        self.assertTupleEqual(OldestTrade[0],(1, '2020-01-01', 'AAPL', 'buy', 100, 12.3))

        newestTrade = dataResults[2]
        self.assertTupleEqual(newestTrade[0],(10, '2020-10-01', 'AAPL', 'sell', 80, 11.3))

        cheapestTrade = dataResults[3]
        self.assertTupleEqual(cheapestTrade[0],(8, '2020-08-01', 'AAPL', 'buy', 100, 6.3))

        ExpensiveTrade = dataResults[4]
        self.assertTupleEqual(ExpensiveTrade[0],(7, '2020-07-01', 'MSFT', 'buy', 100, 16.3))

        mostTrade = dataResults[5]
        self.assertTupleEqual(mostTrade[0],(6, 'AAPL'))

    # If the transaction data with or without query parameters is correct based on the testing data
    def test_listTransactions(self):
        dataController = app.DataController(self.db)
        dataResults = dataController.listTransactions()
        self.assertEqual(len(dataResults[0]),10)
        self.assertIn((1, '2020-01-01', 'AAPL', 'buy', 100, 12.3), dataResults[0])
        self.assertIn((2, '2020-02-01', 'MSFT', 'buy', 80, 8.3), dataResults[0])
        self.assertIn((3, '2020-03-01', 'AAPL', 'sell', 80, 10.3), dataResults[0])
        self.assertIn((4, '2020-04-01', 'MSFT', 'sell', 80, 10.4), dataResults[0])
        self.assertIn((5, '2020-05-01', 'AAPL', 'sell', 100, 9.3), dataResults[0])
        self.assertIn((6, '2020-06-01', 'AAPL', 'buy', 100, 14.3), dataResults[0])
        self.assertIn((7, '2020-07-01', 'MSFT', 'buy', 100, 16.3), dataResults[0])
        self.assertIn((8, '2020-08-01', 'AAPL', 'buy', 100, 6.3), dataResults[0])
        self.assertIn((9, '2020-09-01', 'MSFT', 'sell', 80, 10.3), dataResults[0])
        self.assertIn((10, '2020-10-01', 'AAPL', 'sell', 80, 11.3), dataResults[0])

        dataResults = dataController.listTransactions({"transaction_date":"2020-04-01"})
        self.assertEqual(len(dataResults[0]),1)
        self.assertIn((4, '2020-04-01', 'MSFT', 'sell', 80, 10.4), dataResults[0])

        dataResults = dataController.listTransactions({"symbol":"MSFT"})
        self.assertEqual(len(dataResults[0]),4)

        dataResults = dataController.listTransactions({"symbol":"MSFT","transaction_direction":"buy","Quantity":100})
        self.assertEqual(len(dataResults[0]),1)
        self.assertIn((7, '2020-07-01', 'MSFT', 'buy', 100, 16.3), dataResults[0])

    # if one transaction data can be inserted to the database
    def test_addTransaction(self):
        dataController = app.DataController(self.db)
        dataResults = dataController.addTransaction("2021-01-01","TSLA","buy",150,163.2)
        try:
            conn = sqlite3.connect(self.db)
            result = conn.execute("select * from stocks where symbol like 'TSLA'").fetchall()
            self.assertEqual(len(result),1)
            self.assertTupleEqual(result[0],(11, '2021-01-01', 'TSLA', 'buy', 150, 163.2))
        finally:
            if conn:
                conn.close()


if __name__ == '__main__':
    unittest.main()