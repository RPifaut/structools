# %%
import numpy as np
import pandas as pd
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
import matplotlib.pyplot as plt
import plotly.express as px

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.backtest.backtester import Backtester
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data

l_compo = ["AAPL", "^FCHI", "^SPX"]
N = len(l_compo)
# arr_weights = np.ones(N) * 1/N
arr_weights = np.array([0.6, 0.3, 0.1])

my_basket = Basket.from_params(
    size = 1_000,
    N=1,
    name="EQW Basket",
    worst=False,
    best=False,
    compo=l_compo,
    weights=arr_weights
)

# test_underlying = Underlying()
# print(test_underlying.COMPO)
# print(test_underlying)

start=DateModel(date="2000-01-01")
end=DateModel(date="2020-01-04")
# market = Market.create_market(my_basket.COMPO, start, end)
# print(market.data["^FCHI"])
# df_perf = my_basket.compute_return_compo(start, end)
# print(df)
# df = my_basket.build_track(start, end)
# df.to_excel("Test dataframe.xlsx")
fig = my_basket.plot_track(start, end)
print(type(fig).__name__)
fig.show()