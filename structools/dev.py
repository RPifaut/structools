import numpy as np
from pybacktestchain.data_module import DataModule, get_stocks_data

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data

my_basket = Basket.from_params(
    size = 1_000,
    N=1,
    name="EQW Basket",
    worst=False,
    best=True,
    compo=["AAPL", "MSFT", "AMZN"],
    weights=np.array([0.33, 0.33, 0.33])
)
start=DateModel(date="2000-01-01")
end=DateModel(date="2010-01-01")
market = Market.create_market(my_basket.COMPO, start, end)
print(market.data["AAPL"])
print(start, start.date, start.to_str())
df = my_basket.build_track(start, end)
print(df)
