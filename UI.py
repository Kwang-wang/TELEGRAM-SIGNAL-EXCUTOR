import tkinter as tk
import datetime

class GUI:
    def __init__(self,window):
        self.window = window
        self.window.title("MT5 Telegram signal executor")
        self.window.geometry("600x600")
        
        self.selected_typeTime = tk.IntVar()
        self.selected_typeTime.set(1)
        self.isTPrequired = tk.BooleanVar()
        self.isTPrequired.set(True)
        
        self.frame1 = tk.Frame(padx=20)
        self.frame2 = tk.Frame(padx=20)
        
        self.NotifiText = tk.Text(window, height=13, width=120)
        self.NotifiText.insert(tk.END,"Welcome to MT5 Telegram signal executor\n")
        self.connect_button = tk.Button(window, text="Connect to MT5")
        self.shutdown_button = tk.Button(self.frame1, text="Disconnect to MT5")
        self.BotTokenEntry = tk.Entry(self.frame1, width=30)
        self.BotTokenLabel = tk.Label(self.frame1,text="Bot Token : ")
        self.start_button = tk.Button(self.frame1, text="Start")
        self.stop_button = tk.Button(self.frame1, text="Stop")
        
        self.slippageLabel = tk.Label(self.frame2,text="Slippage(pip) : ")
        self.slippageEntry = tk.Entry(self.frame2, width=20)
        self.volumeLabel = tk.Label(self.frame2,text="Volume : ")
        self.volumeEntry = tk.Entry(self.frame2,width=20)
        
        self.isTPrequired_check = tk.Checkbutton(self.frame2,text="Execute signal without TP",
                                                 variable=self.isTPrequired,onvalue=False,offvalue=True)
        self.pendingRangeLabel = tk.Label(self.frame2,text="close pending order when price exceeds(pip) :")
        self.pendingRangeEntry = tk.Entry(self.frame2,width=5)
        self.MoveSlPointLabel = tk.Label(self.frame1,text="Move sl to entry when profit exceeds (pip) :")
        self.MoveSlPointEntry = tk.Entry(self.frame1,width=5)
        self.CloseLotPointLabel = tk.Label(self.frame1,text="Close Lot when profit exceeds (pip) :")
        self.CloseLotPointEntry = tk.Entry(self.frame1,width=5)
        self.PercentLotCloseLabel = tk.Label(self.frame1,text="Percent Lot Close(%):")
        self.PercentLotClose = tk.Scale(self.frame1,from_=0,to=100,orient=tk.HORIZONTAL)
        self.TrallingStopLabel = tk.Label(self.frame1,text="Trailling Stop :")
        self.TrallingStopEntry = tk.Entry(self.frame1,width=5)
        
        
        self.typeTimeLabel = tk.Label(self.frame2,text="ORDER TIME TYPE CONFIG")
        self.typeTimeop1 = tk.Radiobutton(self.frame2,text="The order stays until manually canceled",
                                          variable=self.selected_typeTime,value=1,command=lambda:self.turnOfTimeSpecified())
        self.typeTimeop2 = tk.Radiobutton(self.frame2,text="The order is active during trading day",
                                          variable=self.selected_typeTime,value=2,command=lambda:self.turnOfTimeSpecified())
        self.typeTimeop3 = tk.Radiobutton(self.frame2,text="Skip order after the specified number of days",
                                          variable=self.selected_typeTime,value=3,command=lambda:self.turnOnTimeSpecified())
        self.timeSpecifiedLabel = tk.Label(self.frame2,text="Days:")
        self.timeSpecifiedEntry = tk.Entry(self.frame2,width=5)
        
        self.startUI()
        
    def startUI(self):
        self.NotifiText.pack(pady=10,padx=10,side="bottom")
        self.NotifiText.config(state="disabled")
        self.connect_button.pack(side="top")
        self.frame1.pack(side="right")
        self.frame2.pack(side="left")
        self.BotTokenLabel.pack(side="top")
        self.BotTokenEntry.pack(side="top")
        self.start_button.pack(side="top",pady=10)
        self.stop_button.pack(side="top")
        self.shutdown_button.pack(side="top",pady=10)
        
        self.slippageLabel.pack(side="top")
        self.slippageEntry.pack(side="top")
        self.volumeLabel.pack(side="top")
        self.volumeEntry.pack(side="top")
        
        self.isTPrequired_check.pack(side="top",padx=10,pady=10)
        self.pendingRangeLabel.pack(side="top",padx=10)
        self.pendingRangeEntry.pack(side="top")
        
        self.MoveSlPointLabel.pack(side="top")
        self.MoveSlPointEntry.pack(side="top")
        self.CloseLotPointLabel.pack(side="top")
        self.CloseLotPointEntry.pack(side="top")
        self.PercentLotCloseLabel.pack(side="top")
        self.PercentLotClose.pack(side="top")
        self.TrallingStopLabel.pack(side="top")
        self.TrallingStopEntry.pack(side="top")
        
        self.typeTimeLabel.pack(side="top")
        self.typeTimeop1.pack(side="top")
        self.typeTimeop2.pack(side="top",padx=10)
        self.typeTimeop3.pack(side="top",padx=10)
        
    
    def Notification(self,message):
        self.NotifiText.config(state='normal')
        self.NotifiText.insert(tk.END,"--------------\n{}\n".format(message))
        self.NotifiText.yview(tk.END)
        self.NotifiText.config(state='disabled')
    def run(self):
        self.window.mainloop()
    def close(self):
        self.window.destroy()
    def getBotToken(self):
        return self.BotTokenEntry.get()
    def getTypeTime(self):
        return self.selected_typeTime.get()
    def turnOnTimeSpecified(self):
        self.timeSpecifiedLabel.pack(side="left",padx=10)
        self.timeSpecifiedEntry.pack(side="left")
    def turnOfTimeSpecified(self):
        self.timeSpecifiedLabel.pack_forget()
        self.timeSpecifiedEntry.pack_forget()
    def getSlippage(self):
        return self.slippageEntry.get()
    def getVolume(self):
        return self.volumeEntry.get()
    def getIsTpRequired(self):
        return self.isTPrequired.get()
    def getExpirationDate(self):
        try:
            days = int(self.timeSpecifiedEntry.get())
        except:
            self.Notification("Days is not valid")
            return None
        expirationDateTime = datetime.datetime.now() + datetime.timedelta(days=days)
        expiration = int(expirationDateTime.timestamp())
        return expiration
    def getPendingRange(self):
        if (self.pendingRangeEntry.get() == ''):
            return None
        try:
            pendingRange = int(self.pendingRangeEntry.get())
            return pendingRange
        except:
            self.Notification("Plz Enter correct pending order range")
    def getMoveSLPoint(self):
        if(self.MoveSlPointEntry.get() == ''):
            return None
        try:
            moveSlpoint = int(self.MoveSlPointEntry.get())
            return moveSlpoint
        except:
            self.Notification("Plz Enter correct MoveSLPoint")
    def getCloseLotPoint(self):
        if(self.CloseLotPointEntry.get() == ''):
            return None
        try:
            closeLotPoint = int(self.CloseLotPointEntry.get())
            return closeLotPoint
        except:
            self.Notification("Plz Enter correct CloseLotPoint")
    def getPercentClose(self):
        try:
            percentLotClose = int(self.PercentLotClose.get())
            return percentLotClose
        except:
            pass
    def getTraillingStop(self):
        if (self.TrallingStopEntry.get() == ''):
            return None
        try:
            traillingstop = int(self.TrallingStopEntry.get())
            return traillingstop
        except:
            self.Notification("Plz Enter correct Trailling Stop")
            
