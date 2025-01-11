# %%
import numpy as np
import pandas as pd
from datetime import date
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
import matplotlib.pyplot as plt
import plotly.express as px

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.backtest.backtester import Backtester, get_all_observations
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data

l_compo = ["AAPL", "^FCHI", "^SPX"]
N = len(l_compo)
# arr_weights = np.ones(N) * 1/N
arr_weights = np.array([0.6, 0.3, 0.1])



my_basket = Basket.from_params(
    size = 1_000,
    N=3,
    name="EQW Basket",
    worst=False,
    best=False,
    compo=l_compo,
    weights=arr_weights
)

start = DateModel(date="2000-01-01")
end = DateModel(date=date.today())
# df = load_stocks_data(l_compo, start, end)
# print(df)
df_track = my_basket.build_track(start, end)[my_basket.name]
last_date = DateModel(date="2005-01-01")
length = 10

arr_start = df_track.index[:np.searchsorted(df_track.index.values, last_date.date)].values
mat_obs, mat_dates = get_all_observations(arr_start, 60, "M", df_track)
df_ret = pd.DataFrame(mat_obs, index=arr_start)
df_dates = pd.DataFrame(mat_dates, index = arr_start)
print(df_ret)
print(df_dates)