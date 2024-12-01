import numpy as np
from pybacktestchain.data_module import DataModule, get_stocks_data

from src.structools.products.basic_products import Option, Underlying
from src.structools.products.autocalls import Phoenix, Athena
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import load_stocks_data

output = load_stocks_data(["AAPL", "MSFT"], DateModel(date="2000-01-01"), DateModel(date="2024-01-01"))

print(output)
print(output.index, output.index.dtype, type(output.index))