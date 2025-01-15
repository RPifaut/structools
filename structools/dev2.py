import numpy as np
from structools.tools.date_tools import DateModel
from structools.products.basic_products import Basket
from structools.products.autocalls import Phoenix, Athena
from structools.backtest.backtester import Backtester

# Underlying creation Worst-Of 2
nominal = 1_000_000
L_COMPO = ["AAPL", "^FCHI", "^SPX", "MSFT"]
N = len(L_COMPO)
arr_weights = np.ones(N) * 1/N
basket_wof = Basket.from_params(
    size=nominal,
    N=2,
    name="WOF2",
    worst=True,
    best=False,
    compo=L_COMPO,
    weights=arr_weights
)

# Create default phoenix with custom underlying
my_phoenix = Phoenix.from_params(underlying=basket_wof)
my_phoenix.set_parameter("coupon", 0.1)                 # Changing the coupon value to 10%

# Configure the backtest - 10 years history for the my_phoenix product
history_length = 10
backtester = Backtester.init_backtester(
    product=my_phoenix,
    backtest_length=history_length,
    investment_horizon=my_phoenix.maturity
)

# Running the backtest
dict_res = backtester.backtest_autocall()