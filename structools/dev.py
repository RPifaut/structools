# %%
import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
# import matplotlib.pyplot as plt
import plotly.express as px

from structools.products.basic_products import Option, Underlying, Basket, Index
from structools.products.autocalls import Autocall, Phoenix, Athena
from structools.backtest.backtester import Backtester, get_all_observations, mono_path_backtest, all_paths_backtest
from structools.tools.date_tools import DateModel, find_dates_index
from structools.tools.market import Market, load_stocks_data

from tests.params import *


# my_index = Index.from_params(100000, name="test", rebal_freq="A", compo=["AAPL", "MSFT"], weights=np.array([0.5, 0.5]))
my_index = Index.from_params(size = 1_000_000, name="Index Test", rebal_freq="A", compo=L_COMPO, weights=WEIGHTS)
df_perf = my_index.compute_return_compo(START_DATE, END_DATE, True)
df_track = my_index.build_track(START_DATE, END_DATE, None)
print(df_track.shape)

# # Backtesting Athena - Phoenix
# dict_athena = DICT_ATHENA.copy()
# dict_athena["underlying"] = INDEX
# athena = Athena.from_params(**dict_athena)
# bt_athena = Backtester.init_backtester(product=athena, backtest_length=10, 
#                                         investment_horizon=athena.maturity)
# res_athena = bt_athena.backtest_autocall()
# print(res_athena)
