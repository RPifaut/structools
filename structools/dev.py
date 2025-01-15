# %%
import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from pybacktestchain.data_module import DataModule, get_stocks_data
import openpyxl
import matplotlib.pyplot as plt
import plotly.express as px

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Autocall, Phoenix, Athena
from src.structools.backtest.backtester import Backtester, get_all_observations, mono_path_backtest, all_paths_backtest
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data



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

print(isinstance(my_basket, Underlying))

start = DateModel(date="2001-10-22")
end = DateModel(date="2024-10-22")
df_ret = my_basket.compute_return_compo(start, end)
df_track = my_basket.build_track(start, end)
print(df_track)
print(df_track.shape)
# my_bt = Backtester.init_backtester(my_phoenix, 10, my_phoenix.maturity)
# res = my_bt.backtest_autocall()
# print(res)
# print(my_bt.market)
# df_ret = my_bt.product.underlying.compute_return_compo(start, end, True, market = my_bt.market)
# df_track = my_bt.product.underlying.build_track(start, end, df_ret)[my_basket.name]
# fig = my_basket.plot_track(start, end)
# fig.show()
# print(df_track)
# END = pd.Timestamp(df_track.index[-1]).to_pydatetime() - relativedelta(years=my_bt.investment_horizon)
# START = END - relativedelta(years=my_bt.investment_horizon + my_bt.backtest_length)
# # END = np.searchsorted(df_track.index, END)
# idx = np.searchsorted(df_track.index, END + relativedelta(years=my_bt.investment_horizon))
# print(df_track.index[idx])
# END = np.searchsorted(df_track.index, END)
# arr_dates = df_track.index[:END]
# print(arr_dates)
# mat_obs, mat_dates, arr_min_val, arr_min_dates = get_all_observations(arr_dates, len(my_bt.product.arr_coupon_trigger), my_bt.product.recall_freq, df_track)

# print(mat_obs[:, 1:])
# print(mat_obs[:, 1:].shape)
# arr_feat = np.zeros((len(my_phoenix.arr_recall_trigger), 4))
# arr_feat[:, 0] = my_phoenix.arr_recall_trigger
# arr_feat[:, 1] = my_phoenix.arr_coupon_trigger
# arr_feat[:, 2] = my_phoenix.arr_coupons

# arr_call = np.array(
#     [
#         my_phoenix.call_strike,
#         my_phoenix.call_leverage,
#         my_phoenix.call_cap
#     ]
# )

# arr_put = np.array(
#     [
#         my_phoenix.put_strike,
#         my_phoenix.put_barrier,
#         my_phoenix.put_leverage,
#         my_phoenix.kg
#     ]
# )

# print(f"""

# matrix in use:
      
      
#       {mat_obs[0, 1:]}""")


# arr_cf, idx, ind_pdi = all_paths_backtest(
#     arr_feat=arr_feat,
#     arr_call=arr_call,
#     arr_put=arr_put,
#     memory=my_phoenix.is_memory,
#     arr_min_val=arr_min_val,
#     put_obs=my_phoenix.put_barrier_observ,
#     mat_obs=mat_obs[:, 1:]
# )

# print(arr_cf)
# print(arr_cf.shape)
# df_feat = pd.DataFrame(arr_feat)
# df_cf = pd.DataFrame(arr_cf, index=arr_dates)
# df_obs = pd.DataFrame(mat_obs, index=arr_dates)
# df_dates = pd.DataFrame(mat_dates, index=arr_dates)

# df_feat.to_excel("Features.xlsx")
# df_cf.to_excel("Cashflows.xlsx")
# df_obs.to_excel("Observations.xlsx")
# df_dates.to_excel('Dates.xlsx')