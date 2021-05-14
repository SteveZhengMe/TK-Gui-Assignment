# This project is a assignment of College.
# Purpose: Practice TK and database connection
# Usage: The user can add a stock record to Sqllite database, and one can search and list the records
# 
# Author: Steve Zheng
# Date: 2021-03-17

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from functools import partial
from datetime import datetime
import os
import sqlite3
from sqlite3 import Error


##
# Validate the input
class Validator:
    # Return error message if the input is not a number (float)
    # Return None if the input is valid
    def isNumber(self,input):
        errMsg = "Please input a number."
        try:
            if input=='NaN':
                return errMsg
            float(input)
        except ValueError:
            return errMsg
        else:
            return None

    # Return error message if the input is blank
    # Return None if the input is valid
    def isEmpty(self, input):
        errMsg = "Value required"
        if input != "":
            return None
        else:
            return errMsg

    # Return error message if the input is not in a "yyyy-MM-dd" format
    # Return None if the input is valid
    def isDate(self, input):
        errMsg = "Please input a date in yyyy-MM-dd format."
        try:
            datetime.strptime(input, "%Y-%m-%d")
        except ValueError:
            return errMsg
        else:
            return None

##
# One label and one combobox
class LabelDDCombo(tk.Frame):
    def __init__(self, parent, labelName="Label Name", entryState="normal", packSide="left", size=(0,0), margin=(0,0),ddItems=[],*args,**kw):
        super().__init__(master=parent, *args, **kw)
        
        # Create label and pack
        self.label = tk.Label(self, text=labelName, font=("Courier",9), fg="#333", anchor="e")
        if size[0] != None:
            self.label.config(width=size[0])
        self.label.pack(side=packSide, padx=(margin[0],0), pady=margin[1])
        
        # Create input and pack
        self.inputValue = tk.StringVar()
        self.input = ttk.Combobox(self, textvariable = self.inputValue, state=entryState, values=ddItems)
        self.input.current(0)
        if size[1] != None:
            self.input.config(width=size[1])
        self.input.pack(side=packSide, padx=(0,margin[0]), pady=margin[1])

    # When the value is invalidate, this handler will display error message.
    # The handler should be .config(text=XXX)
    def setInputErrorHandler(self, handler):
        self.errHandler = handler
    
    # The validator. It will call validator class and loop
    def validator(self):
        validator = Validator()
        for valRules in self.validatorArray:
            #eval()
            validationErrors = validator.isEmpty(self.getDDValue())
            if validationErrors != None:
                # Output the error message to "error handler"
                self.errHandler.config(text=self.label["text"] + " - " + validationErrors)
                return False
        return True

    # When focus, focus the input box
    def focus(self):
        self.input.focus()
    
    # Return the input value
    def getDDValue(self):
        return self.inputValue.get()

    def setValue(self, valueIndex):
        self.input.current(valueIndex)
        
##
# One label and one input box
class LabelInputCombo(tk.Frame):
    def __init__(self, parent, labelName="Label Name", entryState="normal", packSide="left", size=(0,0), margin=(0,0),validateArray=[],*args,**kw):
        super().__init__(master=parent, *args, **kw)
        # validateArray = ["isNumber", "isEmpty"], means the value needs two validation
        self.validatorArray = validateArray
        
        # Create label and pack
        self.label = tk.Label(self, text=labelName, font=("Courier",9), fg="#333", anchor="e")
        if size[0] != None:
            self.label.config(width=size[0])
        self.label.pack(side=packSide, padx=(margin[0],0), pady=margin[1])
        
        # Create input and pack
        self.inputValue = tk.StringVar()
        self.input = tk.Entry(self, textvariable=self.inputValue, state=entryState)
        if size[1] != None:
            self.input.config(width=size[1])
        self.input.pack(side=packSide, padx=(0,margin[0]), pady=margin[1])
    
    # When the value is invalidate, this handler will display error message.
    # The handler should be .config(text=XXX)
    def setInputErrorHandler(self, handler):
        self.errHandler = handler
    
    # The validator. It will call validator class and loop
    def validator(self):
        self.errHandler.config(text="No Error")
        validator = Validator()
        for valRules in self.validatorArray:
            #eval()
            validationErrors = eval("validator." + valRules + "('" + self.inputValue.get() + "')")
            if validationErrors != None:
                # Output the error message to "error handler"
                self.errHandler.config(text=self.label["text"] + " - " + validationErrors)
                self.input.delete(0,"end")
                return False
        return True

    # When focus, focus the input box
    def focus(self):
        self.input.focus()
    
    # Return the input value
    def getInputValue(self):
        return self.inputValue.get()

    def setValue(self, value):
        if self.input["state"].lower() == "disabled":
            self.input.config(state="normal")
            self.input.delete(0,"end")
            self.input.insert(0,value)
            self.input.config(state="disabled")
        self.input.delete(0,"end")
        self.input.insert(0,value)

# Table view
class TreeViewWithScrollBar(tk.Frame):
    def __init__(self, parent, columnsAttr, tableRows=5, *args,**kw):
        super().__init__(master=parent, *args, **kw)
        columns = list(item["colName"] for item in columnsAttr)
        self.treeview = ttk.Treeview(self, height=tableRows, show="headings", columns=columns)
        
        for aColumn in columnsAttr:
            self.treeview.column(aColumn["colName"], width=aColumn["width"], anchor=aColumn["anchor"])
            self.treeview.heading(aColumn["colName"], text=aColumn["colName"])
        
        treeScroll = ttk.Scrollbar(self, orient="vertical",command=self.treeview.yview)
        self.treeview.grid(row=0,column=0)
        treeScroll.grid(row=0,column=1,sticky="NSEW")
        self.treeview.configure(yscrollcommand=treeScroll.set)
    
    def addValues(self,valueArray):
        self.treeview.insert('','end',values=valueArray)

    def clearAll(self):
        self.treeview.delete(*self.treeview.get_children())

    def setValues(self, tupleArray):
        if tupleArray is not None:
            self.clearAll()
            for row in tupleArray[0]:
                self.addValues(row)
    
    def getRecordsCount(self):
        return len(self.treeview.get_children())

##
# A layout to group some elements.
# Support two layouts:
# Use "h" to pack horizontally
# Use "v" to pack vertically
class LayoutFrame(tk.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(master=parent, *args, **kw)
    
    def layout(self, layout, *items):
        if items != None:
            for item in items:
                if layout == "v":
                    item.pack(side='top', pady=5)
                else:
                    item.pack(side='left', padx=5)
        return self

############################# Above are the widgets; Below are the UI design ###########################

##
# "Activity Display" contains two buttons on the top: Summary and Activities
class ActivityDisplayWindow(tk.Frame):
    summaryFrame = None
    activitiesDataTableFrame = None
    dbName = "stocks.db"

    def __init__(self,parent):
        self.parent = parent
        self.parent.resizable(False, False)
        self.windowSelfConfig()
        self.createWidgets()

    def windowSelfConfig(self):
        self.parent.geometry('400x600+20+20')
        self.parent.title("Activities Display")
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)
    
    def onClose(self):
        if messagebox.askokcancel("Quit", "Do you want to quit both two windows?"):
            self.parent.destroy()
            
    def createWidgets(self):
        # self.parent.rowconfigure(0,weight=1)
        self.parent.columnconfigure(0,weight=1)
        topButtonsArea = LayoutFrame(self.parent)
        self.summaryButton = tk.Button(topButtonsArea, text="Summary", command=partial(self.switchButtonOnClick,"summary"))
        self.activitiesButton = tk.Button(topButtonsArea, text="Activities", command=partial(self.switchButtonOnClick,"Activities"))
        topButtonsArea.layout("h",self.summaryButton, self.activitiesButton).grid(row=0,column=0,pady=10)
        self.buildSummaryPage()
    
    def buildSummaryPage(self):
        if self.summaryFrame is None:
            self.summaryFrame = LayoutFrame(self.parent)
            self.uniqueStockSymbols = tk.StringVar()

            self.oldestTransactionSummary = LabelInputCombo(self.summaryFrame, labelName="Oldest Transaction:", entryState="disabled", size=(22,22), margin=(2,2))
            self.newestTransactionSummary = LabelInputCombo(self.summaryFrame, labelName="Newest Transaction:", entryState="disabled", size=(22,22), margin=(2,2))
            self.cheapestPriceSymmary = LabelInputCombo(self.summaryFrame, labelName="Cheapest Price:", entryState="disabled", size=(22,22), margin=(2,2))
            self.mostExpensivePriceSummary = LabelInputCombo(self.summaryFrame, labelName="Most Expensive Price:", entryState="disabled", size=(22,22), margin=(2,2))
            self.mostTradedStockSummary = LabelInputCombo(self.summaryFrame, labelName="Most Traded Stock:", entryState="disabled", size=(22,22), margin=(2,2))
            
            self.summaryFrame.layout("v",
                tk.Label(self.summaryFrame, text="", font=("Arial", 14), anchor="w"),
                tk.Label(self.summaryFrame, text="Unique Stock Symbols", font=("Arial", 14), anchor="w"),
                tk.Listbox(self.summaryFrame, listvariable=self.uniqueStockSymbols),
                tk.Label(self.summaryFrame, text="", font=("Arial", 14), anchor="w"),
                tk.Label(self.summaryFrame, text="Summary", font=("Arial", 14), anchor="w"),
                self.oldestTransactionSummary,
                self.newestTransactionSummary,
                self.cheapestPriceSymmary,
                self.mostExpensivePriceSummary,
                self.mostTradedStockSummary
                )
        self.summaryFrame.grid(row=1,column=0)
        self.updateInfo()

    def buildActivitiesPage(self):
        if self.activitiesDataTableFrame is None:
            self.activitiesDataTableFrame = TreeViewWithScrollBar(self.parent,[
                {"colName":"ID","width":10,"anchor":"center"},
                {"colName":"Date","width":100,"anchor":"center"},
                {"colName":"Symbol","width":80,"anchor":"center"},
                {"colName":"Transation","width":70,"anchor":"center"},
                {"colName":"Quantity","width":70,"anchor":"center"},
                {"colName":"Price$","width":60,"anchor":"center"}],tableRows=26)
        self.activitiesDataTableFrame.grid(row=1,column=0)
        self.updateInfo()

    # Update the data from DB
    def updateInfo(self):
        dataController = DataController(self.dbName)

        if self.summaryFrame is not None:
            summaryResults = dataController.getSummaryInfo()
            if summaryResults is not None:
                tradeSymbols = summaryResults[0]
                self.uniqueStockSymbols.set([x[0] for x in tradeSymbols])

                OldestTrade = summaryResults[1][0]
                self.oldestTransactionSummary.setValue("%s %s %s" % (OldestTrade[1],OldestTrade[3],OldestTrade[2]))

                newestTrade = summaryResults[2][0]
                self.newestTransactionSummary.setValue("%s %s %s" % (newestTrade[1],newestTrade[3],newestTrade[2]))

                cheapestTrade = summaryResults[3][0]
                self.cheapestPriceSymmary.setValue("$%0.2f %s %s" % (cheapestTrade[5],cheapestTrade[3],cheapestTrade[2]))

                expensiveTrade = summaryResults[4][0]
                self.mostExpensivePriceSummary.setValue("$%0.2f %s %s" % (expensiveTrade[5],expensiveTrade[3],expensiveTrade[2]))

                mostTrade = summaryResults[5][0]
                self.mostTradedStockSummary.setValue("%s (%d Transactions)" % (mostTrade[1],mostTrade[0]))
        
        if self.activitiesDataTableFrame is not None:
            self.activitiesDataTableFrame.setValues(dataController.listTransactions())

    def switchButtonOnClick(self, activity):
        if activity.lower() == "summary":
            if self.activitiesDataTableFrame is not None:
                self.activitiesDataTableFrame.grid_forget()
            self.buildSummaryPage()
        elif activity.lower() == "activities":
            if self.summaryFrame is not None:
                self.summaryFrame.grid_forget()
            self.buildActivitiesPage()

##
# "Activity Display" contains two buttons on the top: Summary and Activities
class ActivityEntryWindow(tk.Frame):
    # will be overwritten in class constructor
    dbName = "stocks_test.db"

    def __init__(self,parent, parentWindowClass):
        self.parent = parent
        self.parentClass = parentWindowClass
        self.dbName = parentWindowClass.dbName
        self.parent.resizable(False, False)
        self.windowSelfConfig()
        self.createWidgets()

    def windowSelfConfig(self):
        self.parent.geometry('400x600+450+20')
        self.parent.title("Activity Entry")
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

    # Destroy parent window
    def onClose(self):
        if messagebox.askokcancel("Quit", "Do you want to quit both two windows?"):
            self.parentClass.parent.destroy()
            
    def createWidgets(self):
        self.errorMessageDisplay = tk.Label(self.parent, text="No Error", font=("Arial", 10), fg="red", anchor="w")
        self.dataInputForm().pack(side="top", pady=(20,10))
        self.buttons().pack(side="top", pady=(0,20))
        tk.Label(self.parent, text="All Transactions", font=("Arial", 14), anchor="w").pack(side="top")
        self.allTransactions = TreeViewWithScrollBar(self.parent,[
                {"colName":"ID","width":10,"anchor":"center"},
                {"colName":"Date","width":100,"anchor":"center"},
                {"colName":"Symbol","width":80,"anchor":"center"},
                {"colName":"Transation","width":70,"anchor":"center"},
                {"colName":"Quantity","width":70,"anchor":"center"},
                {"colName":"Price","width":60,"anchor":"center"}],tableRows=19)
        self.allTransactions.pack(side="top", pady=(10,0), fill="both")
        self.errorMessageDisplay.pack(side="bottom", fill="x")
        self.updateTransactions()

    def dataInputForm(self):
        dataInputFrame = LayoutFrame(self.parent)

        self.dateInput = LabelInputCombo(dataInputFrame, labelName="Date", validateArray=["isDate", "isEmpty"], size=(5,10), packSide="top", margin=(1,1))
        self.dateInput.setInputErrorHandler(self.errorMessageDisplay)
        self.symbolInput = LabelInputCombo(dataInputFrame, labelName="Symbol", validateArray=["isEmpty"], size=(6,6), packSide="top", margin=(2,2))
        self.symbolInput.setInputErrorHandler(self.errorMessageDisplay)
        self.transationInput = LabelDDCombo(dataInputFrame, labelName="Transation", ddItems=["","buy","sell"], size=(10,5),entryState="readonly",packSide="top", margin=(2,2))
        self.transationInput.setInputErrorHandler(self.errorMessageDisplay)
        self.quantityInput = LabelInputCombo(dataInputFrame, labelName="Quantity", validateArray=["isNumber", "isEmpty"], size=(8,8), packSide="top", margin=(2,2))
        self.quantityInput.setInputErrorHandler(self.errorMessageDisplay)
        self.priceInput = LabelInputCombo(dataInputFrame, labelName="Price", validateArray=["isNumber", "isEmpty"], size=(5,6), packSide="top", margin=(2,2))
        self.priceInput.setInputErrorHandler(self.errorMessageDisplay)
        
        dataInputFrame.layout('h',
            self.dateInput,
            self.symbolInput,
            self.transationInput,
            self.quantityInput,
            self.priceInput
        )
        return dataInputFrame

    def buttons(self):
        buttonsFrame = LayoutFrame(self.parent)

        recordButton = tk.Button(buttonsFrame, text="Record", command=self.recordOnClick)
        clearButton = tk.Button(buttonsFrame, text="Clear", command=self.clearOnClick)
        searchButton = tk.Button(buttonsFrame, text="search", command=self.searchOnClick)
        exportButton = tk.Button(buttonsFrame, text="Export", command=self.exportOnClick)

        buttonsFrame.layout('h', recordButton, clearButton, searchButton, exportButton)
        return buttonsFrame

    def updateTransactions(self):
        self.allTransactions.setValues(DataController(self.dbName).listTransactions())

    def generateParametersDict(self):
        queryDict = {}
        if self.dateInput.getInputValue() != "" and self.dateInput.validator():
            queryDict["transaction_date"] = self.dateInput.getInputValue()
        if self.symbolInput.getInputValue() != "" and self.symbolInput.validator():
            queryDict["symbol"] = self.symbolInput.getInputValue()
        if self.transationInput.getDDValue() != "":
            queryDict["transaction_direction"] = self.transationInput.getDDValue()
        if self.quantityInput.getInputValue() != "" and self.quantityInput.validator():
            queryDict["Quantity"] = self.quantityInput.getInputValue()
        if self.priceInput.getInputValue() != "" and self.priceInput.validator():
            queryDict["price"] = self.priceInput.getInputValue()

        return queryDict
        
    def recordOnClick(self):
        inputDict = self.generateParametersDict()
        # 5 means all items are inputted
        if len(inputDict) == 5:
            if DataController(self.dbName).addTransaction(inputDict["transaction_date"],inputDict["symbol"],inputDict["transaction_direction"],inputDict["Quantity"],inputDict["price"]):
                self.updateTransactions()
                self.parentClass.updateInfo()
                self.clearOnClick()
                self.errorMessageDisplay.config(text="Insert Successfully")
            else:
                self.errorMessageDisplay.config(text="Insert Fail.")
        else:
            self.errorMessageDisplay.config(text="Please complete all input items")
        
    def clearOnClick(self):
        self.dateInput.setValue("")
        self.symbolInput.setValue("")
        self.transationInput.setValue(0)
        self.quantityInput.setValue("")
        self.priceInput.setValue("")
        self.errorMessageDisplay.config(text="All inputs are cleared")

    def searchOnClick(self):
        self.allTransactions.setValues(DataController(self.dbName).listTransactions(self.generateParametersDict()))
        self.errorMessageDisplay.config(text=" %d records returned" % self.allTransactions.getRecordsCount())

    def exportOnClick(self):
        destFile = filedialog.asksaveasfile(filetypes = [('Text Document', '*.txt')], defaultextension = [('Text Document', '*.txt')])
        if destFile is not None:
            exportResult = DataController(self.dbName).listTransactions()
            if exportResult:
                destFile.write("User Activity")
                for record in exportResult[0]:
                    destFile.write("\n%d, %s, %s, %s, %d, %.2f" % record)
            destFile.close()
            self.errorMessageDisplay.config(text="Export Successfully")

        
################################# Above are UI design, below are database access code ########################

##
# Controller: Manipulate the data and return to View
class DataController:
    def __init__(self, dataFile):
        self.db = dataFile
        if not os.path.exists(dataFile):
            # Create Data
            if not self.initializeDatabase(withData = True):
                raise Exception("Database Initialize Error")

    # get all information in one connection
    def getSummaryInfo(self):
        isSuccess, dataResult = self.runSql([
            'select distinct symbol from stocks',
            'select * from stocks order by transaction_date asc limit 1',
            'select * from stocks order by transaction_date desc limit 1',
            'select * from stocks order by price asc limit 1',
            'select * from stocks order by price desc limit 1',
            'select count(id) as trade_times, symbol from stocks group by symbol order by trade_times desc limit 1'
            ])
        if isSuccess:
            return dataResult
        return None

    def listTransactions(self, paramDict={}):
        queryParam = []
        for item, value in paramDict.items():
            if type(value) is str:
                queryParam.append(item + "='" + value + "'")
            else:
                queryParam.append(item + "=" + str(value))
        
        where = ""
        if len(queryParam) > 0:
            where = "where " + " and ".join(queryParam)

        # TODO: put it in debug log
        #print('select * from stocks ' + where + ' order by transaction_date asc')
        isSuccess, dataResult = self.runSql([
            'select * from stocks ' + where + ' order by transaction_date asc'
            ])
        if isSuccess:
            return dataResult
        return None

    def addTransaction(self, transDate,symbol,trans,quantity,price):
        isSuccess, dataResult = self.runSql(
            ["insert into stocks (transaction_date,symbol,transaction_direction,Quantity,price) values (?,?,?,?,?)"],
            [(transDate, symbol, trans, quantity, price)]
        )
        return isSuccess

    # Run sql, support batch
    # return 1: True/False for update/delete/insert
    # return 2: fetch data for select
    def runSql(self, sqlStatementArray, sqlStatementParamArray=[]):
        conn = None
        if len(sqlStatementParamArray) > 0:
            if len(sqlStatementArray) != len(sqlStatementParamArray):
                return False,[]

        fetchResult = []
        try:
            conn = sqlite3.connect(self.db)
            needCommit = False
            for i in range(len(sqlStatementArray)):
                if len(sqlStatementParamArray) > 0:
                    queryResults = conn.execute(sqlStatementArray[i], sqlStatementParamArray[i])
                else:
                    queryResults = conn.execute(sqlStatementArray[i])

                if sqlStatementArray[i].strip().lower().startswith("select"):
                    fetchResult.append(queryResults.fetchall())
                else:
                    needCommit = True

            if needCommit:
                conn.commit()
        except Error as e:
            # TODO: Log the error
            print(e)
            return False, []
        else:
            return True, fetchResult
        finally:
            if conn:
                conn.close()

    # Create Table and initialize Data
    # Transaction Data: yyyy-MM-dd
    # Stock Symbol: MSFT
    # Transaction: Buy/Sell
    # Quantity: 100
    # Transation Price: 12.34
    def initializeDatabase(self, withData = False):
        if self.runSql(['''CREATE TABLE stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date DATE,
            symbol text,
            transaction_direction text,
            Quantity INTEGER,
            price REAL
            )'''])[0]:
            return self.runSql(
                ["insert into stocks (transaction_date,symbol,transaction_direction,Quantity,price) values (?,?,?,?,?)" for x in range(10)],
                [
                    ('2020-01-01', 'AAPL', 'buy', 100, 12.3),
                    ('2020-02-01', 'MSFT', 'buy', 80, 8.3),
                    ('2020-03-01', 'AAPL', 'sell', 80, 10.3),
                    ('2020-04-01', 'MSFT', 'sell', 80, 10.4),
                    ('2020-05-01', 'AAPL', 'sell', 100, 9.3),
                    ('2020-06-01', 'AAPL', 'buy', 100, 14.3),
                    ('2020-07-01', 'MSFT', 'buy', 100, 16.3),
                    ('2020-08-01', 'AAPL', 'buy', 100, 6.3),
                    ('2020-09-01', 'MSFT', 'sell', 80, 10.3),
                    ('2020-10-01', 'AAPL', 'sell', 80, 11.3)
                ]
            )[0]
        
        return False

if __name__ == "__main__":
    activityDisplayWindow = tk.Tk()
    displayWindowClass = ActivityDisplayWindow(activityDisplayWindow)
        
    activityEntryWindow = tk.Toplevel(activityDisplayWindow)
    ActivityEntryWindow(activityEntryWindow, displayWindowClass)
        
    activityDisplayWindow.mainloop()