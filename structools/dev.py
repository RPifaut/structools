from src.structools.products.basic_products import Option
from src.structools.tools.date_tools import DateModel
import numpy as np

option_type = "call"
strike_date = DateModel(date="2000-10-10")
spot = 105.0
strike_price=100.0
rate=0.0001
div=0.0009
vol=0.3
ttm = 3

my_option = Option.from_params(option_type, strike_date, spot, strike_price, rate, div, vol, ttm)
print(my_option, type(my_option).__name__)
print(my_option.strike_date.date)