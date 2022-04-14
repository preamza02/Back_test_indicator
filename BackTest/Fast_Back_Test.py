import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

class Fast_Back_Test():
    def __init__(self,price_data,init_money = 10000):# price_data format is pandasDataframe(columns = ['date','price'])
        self.init_money = init_money
        self.money = init_money
        self.price_data = price_data.copy()
        self.hold_position = []
        self.asset = 0
        self.create_signal()

    @abstractmethod
    def create_indicator_H(self,days): #you need to create this fuciton
        self.indicator_H = np.array([])

    @abstractmethod
    def create_indicator_L(self,days): #you need to create this fuciton
        self.indicator_L = np.array([])

    def create_signal(self):#this can be change depend on indicator
        self.create_indicator_H()
        self.create_indicator_L()
        buy_signal = self.indicator_H > self.indicator_L
        signal = []
        state = None
        for isBuy in buy_signal:
            if isBuy and state != 'Hold':
                signal.append('BUY')
                state = 'Hold'
            elif not isBuy and state == 'Hold':
                signal.append("SELL")
                state = None
            else:
                signal.append('NOTHING')
        self.price_data.loc[:,'signal'] = signal

    
    def update_asset_value(self,date):
        if len(self.hold_position) !=0:
            today_price = self.price_data[self.price_data['date'] == date]['price'].values[0]
            self.asset = 0
            for position in self.hold_position: #(date,position_number,size,hold_price)
                self.asset += position[2]*today_price #size*today_price
        else:
            self.asset = 0

    
    def buy(self,date,amount): # amount is how much money
        if amount == -1:
            amount = self.money
        buy_price = self.price_data[self.price_data['date'] == date]['price'].values[0]
        position_number = len(self.hold_position) + 1
        if amount <= self.money:
            size = amount/buy_price
            self.money -= amount
            self.hold_position.append((date,position_number,size,buy_price))
        else:
            print('your money is not enough')

    def sell(self,date,amount = -1): #amount interger money or -1 for sell all
        sell_price = self.price_data[self.price_data['date'] == date]['price'].values[0]
        total_position = len(self.hold_position)
        if total_position == 0:
            print('error you dont have postion') 
        else:
            if amount == -1:
                for position in self.hold_position: # (date,position_number,size,hold_price)
                    self.money += position[2]*sell_price
                self.hold_position = []
            else :
                # let thing about it later
                pass

    def process(self,show_grab = True):
        self.create_signal()
        for index,rows in self.price_data.iterrows():
            day = rows['date']
            signal = rows['signal']
            if signal == 'BUY':
                self.buy(day,-1)
            elif signal == 'SELL':
                self.sell(day,-1)
            else:
                pass
        self.update_asset_value(day)
        self.total_asset_value = self.money + self.asset
        self.total_profit = (100 * (self.money + self.asset)/self.init_money)-100
        print(f'total_assert_value : {self.total_asset_value}')
        print(f"total_profit = {(100 * (self.money + self.asset)/self.init_money)-100} %")


class EMA_Fast_Back_Test(Fast_Back_Test):
    def __init__(self,price_data,EMA_H,EMA_L,init_money = 10000):
        self.EMA_H = EMA_H
        self.EMA_L = EMA_L
        super().__init__(price_data,init_money = init_money)
        
    def create_indicator_H(self):
        self.indicator_H = talib.EMA(self.price_data['price'],self.EMA_H)
        self.indicator_H_name = f'EMA {self.EMA_H}'

    def create_indicator_L(self):
        self.indicator_L = talib.EMA(self.price_data['price'],self.EMA_L)
        self.indicator_L_name = f'EMA {self.EMA_L}'
