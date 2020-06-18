'''
Created on Apr 14, 2020

@author: Ryder
'''
import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from tkinter import ttk
import os

class Dashboard:
    
    def __init__(self):    
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.createGraphic()
        self.loadData(os.path.dirname(os.path.realpath(__file__)) + '\VIPR_DELTA_STATS.xlsx', None, None)
        self.loadData(os.path.dirname(os.path.realpath(__file__)) + '\VIPR_DELTA_STATS.xlsx', None, None)
        self.loadStatusData()
        self.root.configure(background = 'white')
        self.frame.config(background = 'white')
    
    def createGraphic(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Modes", command=self.askForData)
        filemenu.add_command(label="Open Sites", command=self.askForData)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)
        
        self.frame.grid(sticky='NSEW', column=0, row=0)
        tk.Grid.columnconfigure(self.root, 2, weight=1)
        tk.Grid.columnconfigure(self.root, 1, weight=1)
        tk.Grid.rowconfigure(self.root, 5, weight=1)
    
    def askForData(self):
        self.inWindow = inputWindow()
        self.inWindow.display()
        
    def loadNewData(self, inputWindow):
        self.loadData(inputWindow.file_path, inputWindow.startDate, inputWindow.endDate)
        
    def openFile(self):
        file_path, dataType, startDate, endDate = self.inWindow.getData()
        columnNum = 1
        self.loadData(file_path, dataType, columnNum, startDate, endDate)
        
    def loadData(self, filePath, startDate, endDate):
        xl = pd.ExcelFile(filePath)
        dfs = {sheet: xl.parse(sheet) for sheet in xl.sheet_names} 
        modesX = []
        modesY = []
        sitesX = []
        sitesY = []
        
        #Add all days to X between start date and end date
        appendAllDates = False
        if startDate != None and endDate != None:
            delta = endDate - startDate
            for i in range(delta.days + 1):
                day = startDate + timedelta(days=i)
                modesX.append(day)
                sitesX.append(day)
        else:
            appendAllDates = True
            
        if appendAllDates:
            for i in range(len(dfs['Sheet1']['COMMENTS'])):
                comment = dfs['Sheet1']['COMMENTS'][i]
                date = dfs['Sheet1']['END_DATE'][i]
                if comment == 'DATAMINER':
                    modesY.append(dfs['Sheet1']['NUM_NEW_INTS'][i])
                    modesX.append(date)
                if comment == 'GEOMINER':
                    sitesY.append(dfs['Sheet1']['NUM_NEW_INTS'][i])
                    sitesX.append(date)
        else:
            #Add all days to X between start date and end 
            delta = endDate - startDate
            for i in range(delta.days + 1):
                day = startDate + timedelta(days=i)
                modesX.append(day)
                sitesX.append(day)
            for i in range(len(modesX)):
                for j in range(len(dfs['Sheet1']['date'])):
                    date = dfs['Sheet1']['END_DATE'][j]
                    if date == modesX[i]:
                        comment = dfs['Sheet1']['COMMENTS'][i]
                        if comment == 'DATAMINER':
                            modesY.append(dfs['Sheet1']['NUM_NEW_INTS'][j])
                        if comment == 'GEOMINER':
                            sitesY.append(dfs['Sheet1']['NUM_NEW_INTS'][j])
                
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.yticks(range(0,max(modesY)+1))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        plt.ylabel("Num Modes")
        plt.xlabel("Run Date")
        ax.set_facecolor('xkcd:light grey')
        ax.plot(modesX,modesY)
        ax.autoscale(enable=True) 
        fig.autofmt_xdate()
        fig.suptitle("Modes")
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=7, sticky='s')
        
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.yticks(range(0,max(sitesY)+1))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        plt.ylabel("Num Sites")
        plt.xlabel("Run Date")
        ax.set_facecolor('xkcd:light grey')
        ax.plot(sitesX,sitesY)
        ax.autoscale(enable=True) 
        fig.autofmt_xdate()
        fig.suptitle("Sites")
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, rowspan=7, sticky='s')
        
    def loadStatusData(self):
        f = open(os.path.dirname(os.path.realpath(__file__)) + "\system.txt", "r")
        label = tk.Label(self.root, text="System Dashboard", fg = "black", bg = "light grey", font = "Verdana 16 bold")
        label.grid(sticky='EW', row=0, columnspan=4)
        label = tk.Label(self.root, text="Statuses", fg = "black", bg = "white", font = "Verdana 12 bold")
        label.grid(row=1)
        statuses = ""
        t = ""
        while t != "End":
            t = f.readline()
            if t == 'End':
                break;
            statuses += t
        label = tk.Label(self.root, text=statuses, fg = "black", bg = "white", font = "Verdana 10")
        label.grid(row=2)
        f.close()
        
        
class inputWindow:
    startDate = datetime.today()
    endDate = datetime.today()
    
    def display(self):
        self.root = tk.Tk()
        frame = tk.Frame(self.root)
        self.startCal=DateEntry(self.root,dateformat=3,width=12, background='white',
                    foreground='white', borderwidth=4,Calendar=datetime.now().year)
        self.endCal=DateEntry(self.root,dateformat=3,width=12, background='white',
                    foreground='white', borderwidth=4,Calendar=datetime.now().year)
        button = tk.Button(self.root, text="Open data", command=self.getFile)
        self.root.configure(background = 'white')
        frame.config(background = 'white')
        
        grid = tk.Frame(frame) 
        tk.Grid.columnconfigure(self.root, 2, weight=1)
        tk.Grid.columnconfigure(self.root, 1, weight=1)
        tk.Grid.rowconfigure(self.root, 5, weight=1)
        frame.grid(sticky='NSEW', column=0, row=0)
        
        button.grid(row=2, columnspan=2)
        label = tk.Label(self.root, text="Start Date:", fg = "black", bg = "white", font = "Verdana 10")
        label.grid(row=0, column=0)
        self.startCal.grid(row=0, column=1)
        label = tk.Label(self.root, text="End Date:", fg = "black", bg = "white", font = "Verdana 10")
        label.grid(row=1, column=0)
        self.endCal.grid(row=1, column=1)
        tk.mainloop()
        
    def getFile(self):
        if self.startCal.get_date() < self.endCal.get_date():
            self.file_path = tk.filedialog.askopenfilename()
            self.root.focus_force()
            if self.file_path != "":
                self.setData()
        else:
            tk.messagebox.showinfo("Input Error", "Start date is not before end date")
            self.root.focus_force()
            
    def setData(self):
        self.startDate = self.startCal.get_date()
        self.endDate = self.endCal.get_date()
        returnData()
        self.root.destroy()
        
    def getData(self):
        return self.file_path, self.startDate, self.endDate
    
dash = Dashboard()

def returnData():
    dash.loadNewData(dash.inWindow)

dash.root.mainloop()
