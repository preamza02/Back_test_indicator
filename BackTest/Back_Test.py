import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod


#you need to create function create_indicator_H and create_indicator_L 
#by default when indicator_H > indicator_L we will buy(long postion)

class Back_Test(ABC): #this is abstract class cannot call
    def __init__(self,price_data,init_money = 10000,show_history = False,show_log = True):# price_data format is pandasDataframe(columns = ['date','price'])
        self.init_money = init_money
        self.money = init_money
        self.price_data = price_data.copy()
        self.hold_position = []
        self.show_history = show_history
        self.asset = 0
        self.show_log = show_log
        self.win_count = 0
        self.loss_count = 0
        if show_history:
            self.history_position = {'date':[],'action':[],'price':[],'money':[],'total_asset_value':[]}
        self.create_signal()

    @abstractmethod
    def create_indicator_H(self,days): #you need to create this fuciton
        self.indicator_H = np.array([])
        self.indicator_H_name = 'indicator_H'

    @abstractmethod
    def create_indicator_L(self,days): #you need to create this fuciton
        self.indicator_L = np.array([])
        self.indicator_L_name = 'indicator_L'

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
            if self.show_log:
                print(f'BUY position date : {date} size : {size} price : {buy_price}')

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
                    if sell_price > position[3]:
                        self.win_count +=1
                    else:
                        self.loss_count += 1
                    if self.show_log:
                        print(f'Sell positionnumber {position[1]} from : {position[0]} size: {position[2]} price : {sell_price} profit {sell_price - position[3]}')
                self.hold_position = []
            else :
                # let thing about it later
                pass


    def show_grab(self):
        day_df = self.price_data['date']
        plt.figure(figsize = (25,10))
        plt.plot(day_df,self.price_data['price'],color = 'blue',label = f'price')
        plt.plot(day_df,self.indicator_L,color = 'green',label = f'{self.indicator_L_name}')
        plt.plot(day_df,self.indicator_H,color = 'red',label = f'{self.indicator_H_name}')
        sell_signal = self.price_data[self.price_data['signal'] == 'SELL']
        buy_signal = self.price_data[self.price_data['signal'] == 'BUY']
        plt.scatter(sell_signal['date'], 'price', data=sell_signal, label='Buy_Signal',marker = 'v', color = 'red')
        plt.scatter(buy_signal['date'], 'price', data=buy_signal, label='Sell_Signal',marker = '^', color = 'green')
        plt.xlabel('Time Line')
        plt.ylabel('Price')
        plt.legend()
        plt.show()


    def process(self,show_grab = True):
        self.create_signal()
        for index,rows in self.price_data.iterrows():
            day = rows['date']
            price = rows['price']
            signal = rows['signal']
            if signal == 'BUY':
                self.buy(day,-1)
                today_action = 'BUY'
            elif signal == 'SELL':
                self.sell(day,-1)
                today_action = 'SELL'
            else:
                today_action = ""
            if self.show_history: # self.history_position = {'date':[],'action':[],'price':[],'money':[],'total_asset_value':[]}
                self.update_asset_value(day)
                self.history_position['date'].append(day)
                self.history_position['action'].append(today_action)
                self.history_position['price'].append(price)
                self.history_position['money'].append(self.money)
                self.history_position['total_assert_value'].append(self.money+self.asset)
        print('\nResult')
        first_day = self.price_data.iloc[0]['date']
        print(f'form {first_day} to {day}')
        self.update_asset_value(day)
        self.total_asset_value = self.money + self.asset
        self.total_profit = (100 * (self.money + self.asset)/self.init_money)-100
        print(f'init money : {self.init_money}')
        print(f"money : {self.money}")
        print(f"asset : {self.asset}")
        print(f'total_asset_value : {self.total_asset_value}')
        print(f"total_profit = {self.total_profit} %")
        total_trade = self.win_count+self.loss_count
        print(f"win_rate = {100 * self.win_count/total_trade} %  total_trade = {total_trade} ")
        first_price = self.price_data.iloc[0]['price']
        last_price = self.price_data.iloc[-1]['price']
        print(f'first price = {first_price} last price = {last_price } change = {(100 * last_price/first_price) -100} %')
        if show_grab:
            self.show_grab()
        


class EMA_Back_Test(Back_Test):
    def __init__(self,price_data,EMA_H,EMA_L,init_money = 10000,show_history = False,show_log  = True):
        self.EMA_H = EMA_H
        self.EMA_L = EMA_L
        super().__init__(price_data,init_money = init_money,show_history = show_history,show_log = show_log)
        
    def create_indicator_H(self):
        self.indicator_H = talib.EMA(self.price_data['price'],self.EMA_H)
        self.indicator_H_name = f'EMA {self.EMA_H}'

    def create_indicator_L(self):
        self.indicator_L = talib.EMA(self.price_data['price'],self.EMA_L)
        self.indicator_L_name = f'EMA {self.EMA_L}'

