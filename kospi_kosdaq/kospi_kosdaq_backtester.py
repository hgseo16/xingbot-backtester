import pymysql
import os
from dotenv import load_dotenv

class Backtest_Engine:

    def __init__(self, table, time_frame, market):
        print('Backtest_Engine Running...')

        # 2천만원
        self.initial_capital = 20000000.0
        self.available_capital = self.initial_capital

        # Final Result
        self.end_capital = None

        # Boolean for whether stock is being held or not
        self.stock_held = False
        self.stock_held_percentage = 0.0

        # Number of stocks bought
        self.num_bought = 0
        # Amount of stocks bought in won value
        self.amount_bought = 0.0

        # Comission fees default to 1%
        self.commission_fee = 0.01
        # self.start_date = None
        # self.end_date = datetime.datetime.now()

        self.cnt = 0

        load_dotenv()

        AUTHENTICATION_PASSWORD = os.environ.get('AUTHENTICATION_PASSWORD')

        conn = pymysql.connect(host='127.0.0.1', user='root', password=AUTHENTICATION_PASSWORD, db='{}_{}'.format(market, time_frame), charset='utf8')

        try:
            curs = conn.cursor()
            query_text = 'SELECT * FROM {}'.format(table)
            curs.execute(query_text)
            self.rs = curs.fetchall()

        finally:
            conn.close()

        self.Strategy()


    def get_SMA(self, SMA_list, size):
        i = len(SMA_list)
        window = SMA_list[i-size:]

        return sum(window) / size


    def Strategy(self):
        start = False
        yesterday_price = 0
        SMA_3_list = []
        SMA_5_list = []
        SMA_10_list = []
        SMA_20_list = []
        SMA_3 = 0
        SMA_5 = 0
        SMA_10 = 0
        SMA_20 = 0

        for idx, row in enumerate(self.rs):
            print("{}th loop: ".format(idx))
            curr_price = row[1]
            # row(1) is the closing price (가격)
            SMA_3_list.append(row[1])
            SMA_5_list.append(row[1])
            SMA_10_list.append(row[1])
            SMA_20_list.append(row[1])

            # Maintains list size according to SMA
            if len(SMA_3_list) > 3:
                del SMA_3_list[0]
            if len(SMA_5_list) > 5:
                del SMA_5_list[0]
            if len(SMA_10_list) > 10:
                del SMA_10_list[0]
            if len(SMA_20_list) > 20:
                del SMA_20_list[0]

            # Calculate SMAs
            if len(SMA_3_list) == 3:
                SMA_3 = self.get_SMA(SMA_20_list, 3)
            if len(SMA_5_list) == 5:
                SMA_5 = self.get_SMA(SMA_20_list, 5)
            if len(SMA_10_list) == 10:
                SMA_10 = self.get_SMA(SMA_20_list, 10)
            if len(SMA_20_list) == 20:
                SMA_20 = self.get_SMA(SMA_20_list, 20)

            if yesterday_price != 0:
                percentage_change = round((-1.0 + (row[1] / yesterday_price)), 2)

            # While stock is being held...
            if self.stock_held == True:
                # percentage_change is 등락률 or % change for the day
                self.stock_held_percentage += (percentage_change)
                print("당일등락률: {}".format(percentage_change))
                print("보유종목등락률: {}".format(self.stock_held_percentage))

            # Buy Condition
            if (SMA_3 != 0) and (self.stock_held == False) and ((curr_price > float(SMA_3)) or (curr_price > float(SMA_5)) or (curr_price > float(SMA_10))):
                if self.available_capital < row[2]:
                    continue
                self.stock_held = True
                # temp = self.available_capital // row[1]
                print("available_capital: {}".format(self.available_capital))
                print("row[1]: {}".format(row[1]))
                print('self.available_capital // row[1]: {}'.format(self.available_capital // row[1]))

                self.num_bought = int(self.available_capital // row[1])
                self.amount_bought = round(self.num_bought * row[1])
                self.available_capital -= self.amount_bought
                print('--------------------')
                print('BOUGHT: {}'.format(row[0]))
                print("available_capital: {}".format(self.available_capital))
                print("num_bought: {}".format(self.num_bought))
                print("amount_bought: {}".format(self.amount_bought))

            # Sell Condition
            # Sell Condition
            # if (self.stock_held == True) and ((curr_price <= float(SMA_3)) and (curr_price <= float(SMA_5)) and (curr_price <= float(SMA_10))):
            if (self.stock_held == True) and ((curr_price <= float(SMA_20)) or self.stock_held_percentage <= -1.0):

                self.stock_held = False

                gain = round(self.amount_bought * (1 + self.stock_held_percentage))
                self.available_capital += gain
                self.num_bought = 0
                self.amount_bought = 0.0
                print('--------------------')
                print('SOLD: {}'.format(row[0]))
                print("available_capital: {}".format(self.available_capital))
                print("stock_held_percentage: {}".format(self.stock_held_percentage))
                print("gain: {}".format(gain))
                print("num_bought: {}".format(self.num_bought))
                print("amount_bought: {}".format(self.amount_bought))
                self.stock_held_percentage = 0.0
                self.cnt+=1

            yesterday_price = row[1]

        print('--------------------')
        print('FINAL: {}'.format(row[0]))
        gain = round(self.amount_bought * (1 + self.stock_held_percentage))
        self.available_capital += gain
        print("Total profit: {}".format(self.available_capital))
        print("stock_held_percentage: {}".format(self.stock_held_percentage))
        print("num_bought: {}".format(self.num_bought))
        # print("amount_bought: {}".format(self.amount_bought))
        print("Number of Trades: {}".format(self.cnt))

