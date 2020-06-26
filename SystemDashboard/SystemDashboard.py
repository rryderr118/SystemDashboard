'''
Created on Apr 14, 2020
@author: Ryder
'''
import tkinter as tk
import pandas as pd
import psycopg2
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
        self.loadData(os.path.dirname(os.path.realpath(__file__)) + '\VIPR_DELTA_STATS.xlsx', os.path.dirname(os.path.realpath(__file__)) + '\config.txt', None, None)
        self.loadStatusData()
        self.root.configure(background = 'white')
        self.frame.config(background = 'white')
    
    def createGraphic(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open Data', command=self.askForData)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.root.quit)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label='Show Data', command=self.showDataWindow)
        menubar.add_cascade(label='File', menu=filemenu)
        menubar.add_cascade(label='View', menu=viewmenu)
        self.root.config(menu=menubar)
        
        self.frame.grid(sticky='NSEW', column=0, row=0)
        tk.Grid.columnconfigure(self.root, 2, weight=1)
        tk.Grid.columnconfigure(self.root, 1, weight=1)
        tk.Grid.rowconfigure(self.root, 5, weight=1)
        self.root.geometry('1600x800')
    
    def askForData(self):
        self.inWindow = inputWindow()
        self.inWindow.display()
        
    def showDataWindow(self):
        self.dataWindow = dataWindow()
        self.dataWindow.display(self.modesX, self.modesY, self.sitesX, self.sitesY)
        
    def makeTickChanger(self, modeFig, modeAx, siteFig, siteAx):
        tickFrame = tk.Frame(self.root, bg = 'white')
        tickFrame.grid(row=5, column=0)
        majorScale = tk.Scale(tickFrame, orient='horizontal', bg='white', length=200)
        minorScale = tk.Scale(tickFrame, orient='horizontal', bg='white', length=200)
        majorLabel = tk.Label(tickFrame, text='Major Tick', bg='white', font='Verdana 9')
        minorLabel = tk.Label(tickFrame, text='Minor Tick', bg='white', font='Verdana 9')
        
        def applyModeTickChanges():
            modeAx.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
            modeAx.xaxis.set_minor_locator(mdates.DayLocator())
            modeAx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            modeAx.yaxis.set_major_locator(ticker.MultipleLocator(majorScale.get()))
            modeAx.yaxis.set_minor_locator(ticker.MultipleLocator(minorScale.get()))
            canvas = FigureCanvasTkAgg(modeFig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=1, rowspan=7, sticky='s')
        def applySiteTickChanges():
            siteAx.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
            siteAx.xaxis.set_minor_locator(mdates.DayLocator())
            siteAx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            siteAx.yaxis.set_major_locator(ticker.MultipleLocator(majorScale.get()))
            siteAx.yaxis.set_minor_locator(ticker.MultipleLocator(minorScale.get()))
            canvas = FigureCanvasTkAgg(siteFig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=2, rowspan=7, sticky='s')
            
        applyModes = tk.Button(tickFrame, text='Apply to Modes', command=applyModeTickChanges)
        applySites = tk.Button(tickFrame, text='Apply to Sites', command=applySiteTickChanges)
        majorLabel.pack(side='top')
        majorScale.pack(side='top')
        minorLabel.pack(side='top')
        minorScale.pack(side='top')
        applyModes.pack(side='left')
        applySites.pack(side='right')
        
    def loadNewData(self, inputWindow):
        self.loadData(inputWindow.file_path, inputWindow.startDate, inputWindow.endDate)
        
    def openFile(self):
        file_path, dataType, startDate, endDate = self.inWindow.getData()
        columnNum = 1
        self.loadData(file_path, dataType, columnNum, startDate, endDate)
        
    def formatY(self, yRange):
        if yRange <= 40:
            return 5
        if yRange > 40 and yRange <= 100:
            return 10
        if yRange > 100 and yRange <= 200:
            return 20
        if yRange > 200 and yRange <= 300:
            return 30
        if yRange > 300 and yRange <= 400:
            return 40
        
    def loadData(self, filePath, configPath, startDate, endDate):
        f = open(configPath, 'r')
        user = f.readline().split('=')[1].strip()
        password = f.readline().split('=')[1].strip()
        host = f.readline().split('=')[1].strip()
        port = f.readline().split('=')[1].strip()
        database = f.readline().split('=')[1]
        print(user,password,host,port,database)
        conn = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        cursor = conn.cursor()
        cursor.execute('SELECT END_DATE, NUM_NEW_INTS, COMMENTS from VIPR_DELTA_STATS')
        results = cursor.fetchall()
        
        self.modesX = []
        self.modesY = []
        self.sitesX = []
        self.sitesY = []
        for row in results:
            if row[2] == 'DM_RESIDUE_MINER':
                self.modesX.append(row[0])
                self.modesY.append(row[1])
            if row[2] == 'GEO_MINER':
                self.sitesX.append(row[0])
                self.sitesY.append(row[1])
                
        modeFig, modeAx = plt.subplots(figsize=(8, 6))
        plt.yticks(range(0,max(self.modesY)+1))
        modeAx.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        modeAx.xaxis.set_minor_locator(mdates.DayLocator())
        modeAx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        modeAx.yaxis.set_major_locator(ticker.MultipleLocator(self.formatY((min(self.modesY)-max(self.modesY)))))
        modeAx.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        plt.ylabel('Num Modes')
        plt.xlabel('Run Date')
        modeAx.set_facecolor('xkcd:light grey')
        modeAx.plot(self.modesX,self.modesY)
        modeAx.autoscale(enable=True) 
        modeFig.autofmt_xdate()
        modeFig.suptitle('Modes')
        canvas = FigureCanvasTkAgg(modeFig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=7, sticky='ns')
        
        siteFig, siteAx = plt.subplots(figsize=(8, 6))
        if startDate != None and endDate != None:
            xticks = []
            delta = endDate - startDate
            #set xticks to be every day between start day and end day
            for i in range(delta.days + 1):
                xticks.append(startDate + timedelta(days=i))
            plt.xticks(xticks)
            
        plt.yticks(range(0,max(self.sitesY)+1))
        siteAx.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        siteAx.xaxis.set_minor_locator(mdates.DayLocator())
        siteAx.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        siteAx.yaxis.set_major_locator(ticker.MultipleLocator(self.formatY((min(self.sitesY)-max(self.sitesY)))))
        siteAx.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        plt.ylabel('Num Sites')
        plt.xlabel('Run Date')
        siteAx.set_facecolor('xkcd:light grey')
        siteAx.plot(self.sitesX,self.sitesY)
        siteAx.autoscale(enable=True) 
        siteFig.autofmt_xdate()
        siteFig.suptitle('Sites')
        canvas = FigureCanvasTkAgg(siteFig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, rowspan=7, sticky='ns')
        
        self.makeTickChanger(modeFig, modeAx, siteFig, siteAx)
        if conn != None:
            conn.close()
        
    def loadStatusData(self):
        label = tk.Label(self.root, text='System Dashboard', fg='black', bg='light grey', font='Verdana 16 bold')
        label.grid(row=0, columnspan=4, sticky='ew')
        statusFrame = tk.Frame(self.root, bg='white')
        statusFrame.grid(row=1, column=0)
        f = open(os.path.dirname(os.path.realpath(__file__)) + '\system.txt', 'r')
        label = tk.Label(statusFrame, text='Statuses', fg='black', bg='white', font='Verdana 12 bold')
        label.pack(side='top')
        statuses = ''
        t = ''
        while t != 'End':
            t = f.readline()
            if t == 'End':
                break;
            statuses += t
        label = tk.Label(statusFrame, text=statuses, fg='black', bg='white', font='Verdana 10')
        label.pack(side='top')
        f.close()
        
    def makeDataWindow(self, xModeData, yModeData, xSiteData, ySiteData):
        self.majorScale = tk.Scale()
        self.minorScale = tk.Scale()
        
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
        button = tk.Button(self.root, text='Open data', command=self.getFile)
        self.root.configure(background = 'white')
        frame.config(background = 'white')
        
        grid = tk.Frame(frame) 
        tk.Grid.columnconfigure(self.root, 2, weight=1)
        tk.Grid.columnconfigure(self.root, 1, weight=1)
        tk.Grid.rowconfigure(self.root, 5, weight=1)
        frame.grid(sticky='NSEW', column=0, row=0)
        
        button.grid(row=2, columnspan=2)
        label = tk.Label(self.root, text='Start Date:', fg = 'black', bg = 'white', font = 'Verdana 10')
        label.grid(row=0, column=0)
        self.startCal.grid(row=0, column=1)
        label = tk.Label(self.root, text='End Date:', fg = 'black', bg = 'white', font = 'Verdana 10')
        label.grid(row=1, column=0)
        self.endCal.grid(row=1, column=1)
        tk.mainloop()
        
    def getFile(self):
        if self.startCal.get_date() < self.endCal.get_date():
            self.file_path = tk.filedialog.askopenfilename()
            self.root.focus_force()
            if self.file_path != '':
                self.setData()
        else:
            tk.messagebox.showinfo('Input Error', 'Start date is not before end date')
            self.root.focus_force()
            
    def setData(self):
        self.startDate = self.startCal.get_date()
        self.endDate = self.endCal.get_date()
        returnData()
        self.root.destroy()
        
    def getData(self):
        return self.file_path, self.startDate, self.endDate
    
        
class dataWindow():
    
    def display(self, xModeData, yModeData, xSiteData, ySiteData):
        root = tk.Tk()
        tk.Grid.columnconfigure(root, 0, weight=1)
        tk.Grid.columnconfigure(root, 6, weight=1)
        tk.Grid.rowconfigure(root, 1, weight=1)
        root.configure(background='white')
        frame = tk.Frame(root, bg='white')
        frame.grid(sticky='NSEW', column=0, row=0)
        label = tk.Label(root, text='Modes', fg = 'black', bg = 'white', font = 'Verdana 10')
        label.grid(row=0, column=1, columnspan=2, sticky='ns')
        label = tk.Label(root, text='Sites', fg = 'black', bg = 'white', font = 'Verdana 10')
        label.grid(row=0, column=4, columnspan=2, sticky='ns')
        listboxModesX = tk.Listbox(root,height=20,width=10,bg='light grey')
        listboxModesX.grid(row=1, column=1, sticky='ns')
        listboxModesY = tk.Listbox(root,height=20,width=10,bg='light grey')
        listboxModesY.grid(row=1, column=2, sticky='ns')
        listboxSitesX = tk.Listbox(root,height=20,width=10,bg='light grey')
        listboxSitesX.grid(row=1, column=4, sticky='ns')
        listboxSitesY = tk.Listbox(root,height=20,width=10,bg='light grey')
        listboxSitesY.grid(row=1, column=5, sticky='ns')
        for i in range(len(xModeData)):
            listboxModesX.insert(i, xModeData[i])
            listboxModesY.insert(i, yModeData[i])
        for i in range(len(xSiteData)):
            listboxSitesX.insert(i, xSiteData[i])
            listboxSitesY.insert(i, ySiteData[i])
    
    
dash = Dashboard()

def returnData():
    dash.loadNewData(dash.inWindow)

dash.root.mainloop()
