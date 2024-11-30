from src.structools.products.basic_products import Option, Underlying
from src.structools.products.autocalls import Phoenix
from src.structools.tools.date_tools import DateModel
import numpy as np

# Parameters for Options
option_type = "call"
strike_date = DateModel(date="2000-10-10")
spot = 105.0
strike_price=100.0
rate=0.0001
div=0.0009
vol=0.3
ttm = 3

# Parameters for Underlying
size = 1_000_000
name ="my basket"
N = 5
is_worst = True
is_best = False
COMPO = ["AAPL", "JAGLN"]
WEIGHTS = np.array([0.5, 0.5])

my_underlying = Underlying(
    size=size, 
    name=name, 
    WORST=is_worst,
    BEST=is_best,
    COMPO=COMPO,
    WEIGHTS=WEIGHTS
)

print(my_underlying, type(my_underlying), my_underlying.size)