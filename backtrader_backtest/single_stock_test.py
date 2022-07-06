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
        ma_fast = bt.ind.SMA(period = self.params.fast_length)
        ma_slow = bt.ind.SMA(period = self.params.slow_length)

        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)
        print(self.crossover)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()


if __name__ == '__main__':

    cerebro = bt.Cerebro()

    stock = 'AAPL'
    start = '2010-01-01'
    end = '2020-01-01'

    data = bt.feeds.PandasData(
        dataname=yf.download(
            stock,
            start,
            end,
            auto_adjust=True
        )
    )

    cerebro.adddata(data)
    cerebro.addstrategy(MaCrossStrategy)
    cerebro.broker.setcash(1000000.0)
    # cerebro.addsizer(bt.sizers.PercentSizer, percents = 10)

    start_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % start_value)

    cerebro.run()

    end_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % end_value)

    pnl = end_value - start_value
    print('P/L: %.2f' % pnl)

    cerebro.plot()