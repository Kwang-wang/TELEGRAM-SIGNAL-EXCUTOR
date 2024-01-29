from UI import GUI
import tkinter as tk
import MetaTrader5 as mt5
import threading
import telegram.error as er
from telegram.ext import Updater, MessageHandler, Filters
from datetime import datetime,timezone
from order_request import Request as order
from messageFormater import messageFomater as fomater
import time
from retcode import exception
#generate UI
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", lambda:turnOffApp())
ui = GUI(root)

isRunning = False
#function
def connect():
    if not mt5.initialize():
        ui.Notification("initialize() failed, error code =",mt5.last_error())
        return
    terminal_name = mt5.terminal_info().name
    version = mt5.version()
    account_info = mt5.account_info()
    message = "SUCCESSFULLY CONNECTED TO MT5\nMT5 Info: {}\nMT5 version : {}\n".format(terminal_name,version)
    message =message+ "Account number : {}\nLeverage : {}\nBalance : {}\nServer :{}\nCurency : {}\n".format(account_info.login,account_info.leverage,account_info.balance,account_info.server,account_info.currency)
    ui.Notification(message)
def shutdown():
    if isRunning:
        orderProcessHandler.stop()
        bot.stop()
    mt5.shutdown()
    ui.close()
    
#BOT
class Listener:
    def __init__(self, bot_token):
        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.date = None
        self.action = None
        self.order = None
        self.symbol = None
        self.volume = None
        self.price = None
        self.stoplimit = None
        self.sl = None
        self.tp = None
        self.devitation = 20
        self.type_filling = mt5.ORDER_FILLING_IOC
        self.type_time = None
        self.slippage = None
        self.expiration = None
        self.comment = None
        self.position = None
        self.position_by = None
        self.type_times = [mt5.ORDER_TIME_GTC,mt5.ORDER_TIME_DAY,mt5.ORDER_TIME_SPECIFIED_DAY]
        
        message_handler = MessageHandler(Filters.text & ~Filters.command, self.handle_message)
        self.dispatcher.add_handler(message_handler)
        
    def handle_message(self, update,context):
        if(update.message.date < self.date.replace(tzinfo=timezone.utc)):
            return
        message_text = update.message.text
        orderInfo = fomater(message_text)
        ui.Notification("recieved text {} : \n{}".format(update.message.date,message_text))
        if not orderInfo.isOrder or orderInfo.price == None:       
            ui.Notification("This message is not order!")
            context.bot.send_message(chat_id=update.effective_chat.id, text="This message is not order!")
            return
        if (ui.getVolume() == ''):
            ui.Notification("plz Enter correct volume")
            context.bot.send_message(chat_id=update.effective_chat.id, text="plz Enter correct volume")
            return
        if (ui.getSlippage() == ''):
            ui.Notification("plz Enter correct slipage")
            context.bot.send_message(chat_id=update.effective_chat.id, text="plz Enter correct slipage")
            return
        self.symbol = orderInfo.symbol
        if (self.symbol == None):
            ui.Notification("No symbols were found")
            context.bot.send_message(chat_id=update.effective_chat.id, text="No symbols were found")
            return
        self.price = orderInfo.price
        self.sl = orderInfo.sl
        self.tp = orderInfo.tp
        if ui.getIsTpRequired() and self.tp == None:
            ui.Notification("TP is required")
            context.bot.send_message(chat_id=update.effective_chat.id, text="TP is required")
            return        
        self.volume = float(ui.getVolume())
        self.slippage = int(ui.getSlippage())
        self.type_time = self.type_times[int(ui.getTypeTime())-1]
        if(self.type_time == mt5.ORDER_TIME_SPECIFIED_DAY):
            self.expiration = ui.getExpirationDate()
        ui.Notification("Account balance : {} |Symbol : {} | Price : {} | SL : {} | TP: {} | Volume : {} lot | Slippage : {} pip"
                        .format(mt5.account_info().balance,self.symbol,self.price,self.sl,self.tp,self.volume,self.slippage))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Account balance : {} |Symbol : {} | Price : {} | SL : {} | TP: {} | Volume : {} lot | Slippage : {} pip"
                        .format(mt5.account_info().balance,self.symbol,self.price,self.sl,self.tp,self.volume,self.slippage))
        neworder = order(symbol=self.symbol,volume=self.volume,price=self.price,sl=self.sl,
                         tp=self.tp,type_time=self.type_time,type_filling=self.type_filling,
                         slippage=self.slippage,devitaion=self.devitation,expiration=self.expiration)
        result = neworder.sendNewOrderrequest()
        ui.Notification(result)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)

        
        

    def run(self):
        # Bắt đầu bot
        self.date = datetime.now(timezone.utc)
        self.updater.start_polling()
        self.updater.idle()
    def stop(self):
        # Dừng bot
        self.updater.stop()
#----------------------------------------------------------------------------------------------------------------
class OrderProcessHandler:
    def __init__(self,pendingRange = None,moveSLPoint = None,traillingStop = None,closeLotPoint = None,volumeClose =None) :
        self.pendingRange = pendingRange
        self.moveSLPoint = moveSLPoint
        self.closeLotPoint = closeLotPoint
        self.volumeClose = volumeClose
        self.traillingStop = traillingStop
        
        self.isrunning = False
        self.isStartTralling = False
    def closePendingOrder(self,order) :
        request ={
            "order": order.ticket,
            "action" : mt5.TRADE_ACTION_REMOVE
        }
        result = mt5.order_send(request)
        return ("retcode :{} : {}".format(str(result.retcode),exception(result.retcode)))
    def checkpendingorder(self,orders):
        if (self.pendingRange == None):
            return
        for order in orders:
            print("checking : order {}".format(order.ticket))
            point = mt5.symbol_info(order.symbol).point
            currentPrice = None
            if order.type == mt5.ORDER_TYPE_BUY_LIMIT:
                currentPrice = mt5.symbol_info_tick(order.symbol).ask
            if  order.type == mt5.ORDER_TYPE_SELL_LIMIT:
                currentPrice = mt5.symbol_info_tick(order.symbol).bid
            if(abs(float(currentPrice - order.price_open)) > float(self.pendingRange * point * 10)):
                result = self.closePendingOrder(order)
                ui.Notification("Close pending order : {} | Symbol : {} | Price Open : {} | CurrentPrice {}\n"
                                .format(order.ticket,order.symbol,order.price_open,currentPrice)+ result)
    
    def closeLot(self,position,percentClose):
        if(position.type == mt5.ORDER_TYPE_BUY):
            price = mt5.symbol_info_tick(position.symbol).ask
            typee = mt5.ORDER_TYPE_SELL
        if(position.type == mt5.ORDER_TYPE_SELL):
            price = mt5.symbol_info_tick(position.symbol).bid
            typee = mt5.ORDER_TYPE_BUY
        volumeclose = float(position.volume/100 * percentClose)
        comment = position.comment + ' closed'
        request ={
            "action" : mt5.TRADE_ACTION_DEAL,
            "position" : position.ticket,
            "symbol" : position.symbol,
            "volume" : volumeclose,
            "type" : typee,
            "price" : price,
            "devitation" : 20,
            "magic" : 100,
            "comment" : comment,
            "type_time" : mt5.ORDER_TIME_GTC,
            "type_filling" : mt5.ORDER_FILLING_IOC
        }
        result = mt5.order_send(request)
        return ("retcode :{} : {}".format(str(result.retcode),exception(result.retcode)))
    def moveSLtoEntry(self,position):
        point = mt5.symbol_info(position.symbol).point
        sl = None
        if(position.type == mt5.ORDER_TYPE_BUY):
            sl = float(position.price_open + 20*point)
        if(position.type == mt5.ORDER_TYPE_SELL):
            sl = float(position.price_open - 20*point)
        request ={
            "action" : mt5.TRADE_ACTION_SLTP,
            "position" : position.ticket,
            "symbol" : position.symbol,
            'sl' : sl
        }
        result = mt5.order_send(request)
        return ("retcode :{} : {}".format(str(result.retcode),exception(result.retcode)))
    
    def traillingStopFunc(self,position,traillingRange):
        point = mt5.symbol_info(position.symbol).point
        sl = None
        price = None
        if(position.type == mt5.ORDER_TYPE_BUY):
            price = mt5.symbol_info_tick(position.symbol).ask
            sl = float(price - 10*point*traillingRange)
        if(position.type == mt5.ORDER_TYPE_SELL):
            price = mt5.symbol_info_tick(position.symbol).bid
            sl = float(price + 10*point * traillingRange)
        request ={
            "action" : mt5.TRADE_ACTION_SLTP,
            "position" : position.ticket,
            "symbol" : position.symbol,
            'sl' : sl
        }
        result = mt5.order_send(request)
        return ("retcode :{} : {}".format(str(result.retcode),exception(result.retcode)))
    
    def checkPosition(self,positions):
        for position in positions:
            print("checking : order {}".format(position.ticket))
            if(position.profit <=0):
                continue
            point = mt5.symbol_info(position.symbol).point
            positiveSL : bool
            if(position.type == mt5.ORDER_TYPE_BUY and position.sl < position.price_open):
                positiveSL = False
            elif(position.type == mt5.ORDER_TYPE_SELL and position.sl > position.price_open):
                positiveSL = False
            else:
                positiveSL = True
            
            if self.closeLotPoint != None and not('closed' in position.comment):
                if (abs(float(position.price_current-position.price_open)) >= self.closeLotPoint * point * 10):
                    result = self.closeLot(position,self.volumeClose)
                    ui.Notification("Close {} percent order : {} | Symbol : {} | Price Open : {} | CurrentPrice {}\n"
                                    .format(self.volumeClose,position.ticket,position.symbol,position.price_open,position.price_current)+ result)
            if self.moveSLPoint != None and not positiveSL:
                if (abs(float(position.price_current-position.price_open)) >= self.moveSLPoint * point * 10):
                    result = self.moveSLtoEntry(position)
                    ui.Notification("Move SL to Entry order : {} | Symbol : {} | Price Open : {} | CurrentPrice {}\n"
                                    .format(position.ticket,position.symbol,position.price_open,position.price_current)+ result)
            if self.traillingStop != None and (abs(float(position.price_current - position.price_open)) > self.traillingStop*10*point) and (abs(float(position.price_current - position.sl)) > self.traillingStop*10*point):
                result = self.traillingStopFunc(position,self.traillingStop)
                ui.Notification("traillingStopped order : {} | Symbol : {} | Price Open : {} | CurrentPrice {}\n"
                                    .format(position.ticket,position.symbol,position.price_open,position.price_current)+ result)
    def run(self):
        self.isrunning = True
        while self.isrunning:
            time.sleep(2)
            print("orderHandler is running")
            positions = mt5.positions_get()
            orders = mt5.orders_get()
            if(orders != None):
                self.checkpendingorder(orders=orders)
            if(positions != None):
                self.checkPosition(positions=positions)
    def stop(self):
        self.isrunning = False
#----------------------------------------------------------------------------------------------------------------
def start():
    bot_token = ui.getBotToken()
    if(bot_token == ''):
        ui.Notification("Pls enter your bot token")
        return
    
    try:
        global bot
        bot = Listener(bot_token)
    except er.InvalidToken:
        ui.Notification("BotToken is not valid")
        return
    bot_thread = threading.Thread(target=connect_to_bot)
    try:
        bot_thread.start()
    except ValueError:
        pass
    #order handler
    pendingRange = ui.getPendingRange()
    moveSLPoint = ui.getMoveSLPoint()
    closeLotPoint = ui.getCloseLotPoint()
    percentClose = ui.getPercentClose()
    traillingStop = ui.getTraillingStop()
    try:
        global orderProcessHandler
        orderProcessHandler = OrderProcessHandler(pendingRange=pendingRange,moveSLPoint=moveSLPoint,closeLotPoint=closeLotPoint,
                                                  volumeClose=percentClose,traillingStop=traillingStop)
    except:
        print("some error orccur")
    orderHandler_thread = threading.Thread(target=runOrderHandler) 
    orderHandler_thread.start()
        
def runOrderHandler():
    orderProcessHandler.run()
def connect_to_bot():
    global isRunning
    if not isRunning:
        ui.Notification("Successfully connected to your bot")
        ui.Notification("Running....")
        isRunning = True
        bot.run()
    else:
        ui.Notification("Bot is already running....")
def stop():
    global isRunning
    if isRunning:
        try:
            orderProcessHandler.stop()
            bot.stop()
        except:
            ui.Notification("Some error orccur...")
        else:
            ui.Notification("Bot stopped...")
            isRunning = False
    else:
        ui.Notification("Bot has not been activated yet")
def turnOffApp():
    global isRunning
    try:
        if isRunning:
            orderProcessHandler.stop()
            bot.stop()
            isRunning = False
        ui.window.destroy()
    except:
        ui.Notification("Some error orccur...")
    else:
        ui.Notification("Bot stopped...")






#SetCommandtoButton
ui.connect_button.config(command=connect)
ui.shutdown_button.config(command= shutdown)
ui.start_button.config(command=start)
ui.stop_button.config(command=lambda:stop())
ui.run()