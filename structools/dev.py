import numpy as np
from pybacktestchain.data_module import DataModule, get_stocks_data

from src.structools.products.basic_products import Option, Underlying
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market

output = Market.create_market(["AAPL", "MSFT"], DateModel(date="2000-01-01"), DateModel(date="2024-01-01"))

print(output)
