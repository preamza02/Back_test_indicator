import talib
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
# data format is pandasDataframe(columns = ['date','price'])


class agent(ABC): #this is abstract class cannot call
    def __init__(self,price_data,init_money = 10000,show_history = False):
        self.money = init_money
        self.price_data = price_data
        self.hold_position = []
        if show_history:
            self.history_position = {'date':[],'action':[],'price':[],'money':[],'total_asset_value':[]}

    def buy(self,date,amount): # amount is how much money
        total_position = len(self.hold_position)
        hold_price = self.price_data['price'][self.price_data['date'] == date]
        self.hold_position.append((date,hold_price))
        print(f'Add postion {total_position}')

    def sell(self,date,amount = -1): #amount interger money or -1 for sell all
        total_position = len(self.hold_position)
        if total_position == 0:
            print('error you dont have postion') 
        else:
            if amount == -1:
                for positon in self.hold_position

    def profit():
        pass


class percent_stoploss_agent(agent):
    def __init__(self,price_data,percent_stoploss = 0.03):
        super(price_data)
