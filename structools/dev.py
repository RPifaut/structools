# %%
import numpy as np
import pandas as pd
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
import matplotlib.pyplot as plt

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.backtest.backtester import Backtester
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data

my_basket = Basket.from_params(
    size = 1_000,
    N=1,
    name="EQW Basket",
    worst=False,
    best=False,
    compo=["AAPL"],
    weights=np.array([1])
)

# test_underlying = Underlying()
# print(test_underlying.COMPO)
# print(test_underlying)

start=DateModel(date="2000-01-01")
end=DateModel(date="2020-01-04")
market = Market.create_market(my_basket.COMPO, start, end)
print(market.data["AAPL"])
df_perf = my_basket.compute_return_compo(start, end)
# print(df)
df = my_basket.build_track(start, end, df_perf)
# df.to_excel("Test dataframe.xlsx")
plt.plot(df)
plt.show()
