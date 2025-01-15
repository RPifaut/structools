# %%
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
from structools.backtest.backtester import Backtester, get_all_observations, mono_path_backtest, all_paths_backtest
from structools.tools.date_tools import DateModel
from structools.tools.market import Market, load_stocks_data

from tests.params import *


# Backtesting Athena - Phoenix
dict_athena = DICT_ATHENA.copy()
dict_athena["underlying"] = BASKET
athena = Athena.from_params(**dict_athena)
bt_athena = Backtester.init_backtester(product=athena, backtest_length=10, 
                                        investment_horizon=athena.maturity)
res_athena = bt_athena.backtest_autocall()
