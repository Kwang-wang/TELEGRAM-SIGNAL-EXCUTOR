import MetaTrader5 as mt5
from retcode import exception

class Request:
    def __init__(self,action = None,order = None, symbol = None,volume = None,
                 price = None,stoplimit = None,sl = None,tp = None
                 ,devitaion = None,type_filling = None,type_time = None,slippage = None,expiration = None):
        self.action = action
        self.order = order
        self.symbol = symbol
        self.volume = volume
        self.price = price
        self.stoplimit = stoplimit
        self.sl = sl
        self.tp = tp
        self.devitation = devitaion
        self.type_filling = type_filling
        self.type_time = type_time
        self.slippage = slippage
        self.expiration = expiration
        self.point = mt5.symbol_info(self.symbol).point
        self.askbid = None
        if(self.sl > self.price):
            self.type = mt5.ORDER_TYPE_SELL
            self.askbid = mt5.symbol_info_tick(symbol).bid
        else:
            self.type = mt5.ORDER_TYPE_BUY
            self.askbid = mt5.symbol_info_tick(symbol).ask
    def sendNewOrderrequest(self):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return(self.symbol, "not found, can not call order_check()")
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol,True):
                return ("symbol_select({}}) failed, exit",self.symbol)
        if(abs(float(self.askbid - self.price)) > float(self.slippage * self.point * 10)):
            self.action = mt5.TRADE_ACTION_PENDING
            if(self.type == mt5.ORDER_TYPE_BUY):
                self.type = mt5.ORDER_TYPE_BUY_LIMIT
            if(self.type == mt5.ORDER_TYPE_SELL):
                self.type = mt5.ORDER_TYPE_SELL_LIMIT
        else:
            self.action = mt5.TRADE_ACTION_DEAL
        return self.sendOrder()
        
    def jsonHandle(self):
        request = {
            "action": self.action,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": self.type,
            "price": self.price,
            "sl": self.sl,
            "deviation": self.devitation,
            "type_time": self.type_time,
            "type_filling": self.type_filling
        }
        
        if (self.tp != None):
            request["tp"] = self.tp
        if (self.type_time == 3 and self.expiration != None):
            request["expiration"] = self.expiration
        return request
    def sendOrder(self):
        request = self.jsonHandle()
        result = mt5.order_send(request)
        return("retcode :{} : {}".format(str(result.retcode),exception(result.retcode)))
    
    
