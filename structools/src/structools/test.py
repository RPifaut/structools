#%%
import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
import matplotlib.pyplot as plt
import plotly.express as px

from structools.products.basic_products import Option, Underlying, Basket
from structools.products.autocalls import Autocall, Phoenix, Athena
# from structools.backtest.backtester import Backtester, get_all_observations, mono_path_backtest, all_paths_backtest
# from structools.tools.date_tools import DateModel
# from structools.tools.market import Market, load_stocks_data
# from tests.params import *



# df_data = load_stocks_data(tickers=["AAPL", "MSFT", "^FCHI", "^SPX"], start_date=DateModel(date="2001-10-22"), end_date=DateModel(date="2024-10-22"))
# print(df_data)
# print(len(set(df_data["ticker"])))
# print(df_data.shape[0])

l_compo = ["AAPL", "^FCHI", "^SPX", "MSFT"]
N = len(l_compo)
arr_weights = np.ones(N) * 1/N
# arr_weights = np.array([0.3, 0.3, 0.4])
my_basket = Basket.from_params(
    size = 1_000,
    N=1,
    name="EQW Basket",
    worst=True,
    best=False,
    compo=l_compo,
    weights=arr_weights
)