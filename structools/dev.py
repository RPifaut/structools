from src.structools.products.basic_products import Option, Underlying
from src.structools.products.autocalls import Phoenix, Athena
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

# Parameters for the Autocall
strike_date = strike_date
underlying = my_underlying
matu = 10
start_recall = 4
recall_freq = "Q"
first_trigger = 1
step_down = 0

coupon = 0.05
coupon_trigger = first_trigger
start_coupon = 1
coupon_freq = "A"
is_memory = True

call_strike = 1
call_leverage = 0
call_cap = 999

put_strike = 1
put_leverage = 0
put_barrier = 0.7
put_barrier_obs = "EUROPEAN"
kg = 0

my_athena = Athena.from_params(
    strike_date, my_underlying, matu, None, start_recall, recall_freq, first_trigger, step_down, coupon, coupon_freq, start_coupon, call_strike,
    call_leverage, call_cap, put_strike, put_barrier, put_leverage, put_barrier_obs, kg
)

my_phoenix = Phoenix.from_params(
    strike_date, underlying, matu, "EUR", start_recall, recall_freq, first_trigger, 0.05, coupon, coupon_trigger, start_coupon, coupon_freq, is_memory, call_strike, call_leverage,
    call_cap, put_strike, put_barrier, put_leverage, put_barrier_obs, kg
)

print(my_athena.arr_recall_trigger)

print(my_phoenix.arr_recall_trigger)



# Print results
print(my_underlying, type(my_underlying), my_underlying.size)


my_underlying.set_parameter("size", 10.5)
# my_underlying.size = 10.5
print(my_underlying.size)
