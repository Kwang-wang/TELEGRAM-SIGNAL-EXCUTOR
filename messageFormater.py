import re
import MetaTrader5 as mt5
class messageFomater:
    def __init__(self,originalMessage):
        self.Message = originalMessage
        self.isOrder = False
        self.price = None
        self.sl = None
        self.tp = None
        self.symbol = None
        
        self.fomat()
        self.findSymBol()
        self.extract()
    def changeLetter(self):
        if 'stl' in self.Message.lower():
            self.Message = re.sub(r'stl', 'SL', self.Message, flags=re.IGNORECASE)
        if 'xx' in self.Message.lower():
            self.Message = re.sub(r'xx', '', self.Message, flags=re.IGNORECASE)
        if 'vàng' in self.Message.lower():
            self.Message = re.sub(r'vàng', 'XAUUSD', self.Message, flags=re.IGNORECASE)
        if 'gold' in self.Message.lower():
            self.Message = re.sub(r'gold', 'XAUUSD', self.Message, flags=re.IGNORECASE)
        if ',' in self.Message:
            self.Message = re.sub(r',', '.', self.Message, flags=re.IGNORECASE)
        self.Message= self.Message.replace(':','')
    def isOrderr(self):
        if 'sl' in self.Message.lower() and 'buy' in self.Message.lower():
            self.isOrder = True
        elif 'sl' in self.Message.lower() and 'sell' in self.Message.lower():
            self.isOrder = True
        else:
            self.isOrder = False
    def findSymBol(self):
        mt5.initialize()
        symbols = mt5.symbols_get()
        for symbol in symbols:
            if symbol.name.lower() in self.Message.lower():
                self.symbol = symbol.name
                return
    def extractNumber(self,message):
        pattern = r'-?\d+(?:\.\d+)?'
        StrNumbers = re.findall(pattern, message)
        FloatNumber = []
        for num in StrNumbers:
            FloatNumber.append(abs(float(num)))
        return FloatNumber
    def splitString(self):
        indexs =[0]
        if 'sl' in self.Message.lower():
            indexs.append(self.Message.lower().find('sl'))
        if 'tp' in self.Message.lower():
            indexs.append(self.Message.lower().find('tp'))
        indexs.append(len(self.Message))
        sorted_indexs = sorted(indexs)
        splits = []
        for i in range(0,len(sorted_indexs)-1):
            splits.append(self.Message[sorted_indexs[i]:sorted_indexs[i+1]])
        return splits
    def extract(self):
        splits = self.splitString()
        for split in splits:
            if(len(self.extractNumber(split)) == 1):
                if 'sl' in split.lower():
                    self.sl = self.extractNumber(split)[0]
                    continue
                if 'tp' in split.lower():
                    self.tp = self.extractNumber(split)[0]
                    continue
                self.price = self.extractNumber(split)[0]
                continue
            if(len(self.extractNumber(split)) == 2):
                self.price = float((self.extractNumber(split)[0] + self.extractNumber(split)[1])/2)
                
        
    def fomat(self):
        self.changeLetter()
        self.isOrderr()
        if not self.isOrder:
            return


