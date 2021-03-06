import yfinance as yf

import backtrader as bt
import backtrader.analyzers as btanalyzers
import matplotlib
from datetime import datetime

class MaCrossStrategy(bt.Strategy):

    params = (
        ('fast_length', 5),
        ('slow_length', 25)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma3 = bt.ind.SMA(self.datas[0], period = 3)
        self.sma5 = bt.ind.SMA(self.datas[0], period = 5)
        self.sma10 = bt.ind.SMA(self.datas[0], period = 10)
        self.sma20 = bt.ind.SMA(self.datas[0], period = 20)

        self.sma_score = 0



    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if not self.position:
            if self.sma20[0] < self.dataclose[0] and (self.sma3[0] < self.dataclose[0] or self.sma5[0] < self.dataclose[0] or self.sma10[0] < self.dataclose[0]):
                self.buy()
        elif self.sma20[0] > self.dataclose[0]:
            self.close()

        # self.log('Close: %.2f' % self.dataclose[0])

class OverNight(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None


    def next(self):
        # order to sell at close price
        self.order = self.buy(data=self.datas[0], coo=False, coc=True)


    def next_open(self):
        # order to buy at open price
        self.order = self.sell(data=self.datas[0], coo=False, coc=True)



if __name__ == '__main__':


    start = '2017-12-19'
    end = '2022-07-07'

    s = '122630.KS'

    data = bt.feeds.PandasData(
        dataname=yf.download(
            s,
            start,
            end,
            auto_adjust=True
        )
    )

    cerebro = bt.Cerebro(cheat_on_open=True)
    cerebro.broker.set_coc(True)

    cerebro.adddata(data)
    cerebro.addstrategy(OverNight)
    cerebro.broker.setcash(1000000.0)
#    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)

    start_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % start_value)

    result = cerebro.run()

    end_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % end_value)

    # print(result[0].analyzers.yearlyreturn.get_analysis())

    rt = (end_value - start_value) / start_value * 100
    print('Returns: %.2f%%' % rt)

    cerebro.plot(style='candlestick')


    # stocks = ['122630.KS', '252670.KS', '229200.KS', '233740.KS', '251340.KS']

    # for s in stocks:
    #     data = bt.feeds.PandasData(
    #         dataname=yf.download(
    #             s,
    #             start,
    #             end,
    #             auto_adjust=True
    #         )
    #     )
    #
    #     cerebro = bt.Cerebro(cheat_on_open=True)
    #     cerebro.broker.set_coc(True)
    #
    #     cerebro.adddata(data)
    #     cerebro.addstrategy(OverNight)
    #     cerebro.broker.setcash(1000000.0)
    #     cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    #     cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='yearlyreturn')
    #
    #     print(s)
    #     start_value = cerebro.broker.getvalue()
    #     print('Starting Portfolio Value: %.2f' % start_value)
    #
    #     result = cerebro.run()
    #
    #     end_value = cerebro.broker.getvalue()
    #     print('Final Portfolio Value: %.2f' % end_value)
    #
    #     # print(result[0].analyzers.yearlyreturn.get_analysis())
    #
    #     rt = (end_value - start_value) / start_value * 100
    #     print('Returns: %.2f%%' % rt)
    #
    #     cerebro.plot(style='candlestick')

