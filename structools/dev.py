import numpy as np
from pybacktestchain.data_module import DataModule, get_stocks_data

from src.structools.products.basic_products import Option, Underlying, Basket
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, load_stocks_data

my_basket = Basket.from_params(
    size = 1_000,
    name="EQW Basket",
    worst=False,
    best=False,
    compo=["AAPL", "MSFT"],
    weights=np.array([0.5, 0.5])
)
start=DateModel(date="2000-01-01")
end=DateModel(date="2010-01-01")
print(start, start.date, start.to_str())
df = my_basket.compute_performance(start_date=DateModel(date="2000-01-01"), end_date=DateModel(date="2020-01-01"))
print(df)
