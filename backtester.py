from dotenv import load_dotenv

from kospi_kosdaq.kospi_kosdaq_backtester import *

import time
import os
import win32com.client as wc

class Main():

    def __init__(self):

        # Login
        load_dotenv()

        ID = os.environ.get('ID')
        PASSWORD = os.environ.get('PASSWORD')
        AUTHENTICATION_PASSWORD = os.environ.get('AUTHENTICATION_PASSWORD')

        # Implement calling for ETF data
        # KODEX 레버리지 (122630)
        Backtest_Engine(table="kodex_레버리지", time_frame="daily", market='kospi')

        # KODEX 200 선물인버스2X (252670)
        Backtest_Engine(table="kodex_200선물인버스2", time_frame="daily", market='kospi')

        # KODEX 코스닥 150 (229200)
        Backtest_Engine(table="kodex_코스닥150", time_frame="daily", market='kosdaq')

        # KODEX 코스닥 150 레버리지 (233740)
        Backtest_Engine(table="kodex_코스닥150레버", time_frame="daily", market='kosdaq')

        # KODEX 코스닥 150선물인버스 (251340)
        Backtest_Engine(table="kodex_코스닥150선물", time_frame="daily", market='kosdaq')


if __name__ == "__main__":
    start = time.time()
    Main()
    end = time.time()
    print(f"Runtime of the program is {end - start}")