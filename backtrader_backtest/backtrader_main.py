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
        self.crossovers = []

        for d in self.datas:
            ma_fast = bt.ind.SMA(d, period = self.params.fast_length)
            ma_slow = bt.ind.SMA(d, period = self.params.slow_length)

            self.crossovers.append(bt.ind.CrossOver(ma_fast, ma_slow))

    def next(self):
        for i, d in enumerate(self.datas):
            if not self.getposition(d).size:
                if self.crossovers[i] > 0:
                    self.buy()
            elif self.crossovers[i] < 0:
                self.close()

if __name__ == '__main__':


    cerebro = bt.Cerebro()
    stocks = ['122630.KS', '252670.KS', '229200.KS', '233740.KS', '251340.KS']
    for s in stocks:
        data = bt.feeds.PandasData(
            dataname=yf.download(
                s, '2015-07-06',
                '2021-07-01',
                auto_adjust=True
            )
        )
        cerebro.adddata(data, name = s)

    cerebro.addstrategy(MaCrossStrategy)
    cerebro.broker.setcash(1000000.0)
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 10)

    start_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % start_value)

    cerebro.run()

    end_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % end_value)

    pnl = end_value - start_value
    print('P/L: %.2f' % pnl)

    cerebro.plot()