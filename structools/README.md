# structools

Helpful tools for QIS and Pricing Structuring teams

## Installation

```bash
$ pip install structools
```

## Usage

Every new functionality developed in this package has been interfaced so you have very little to do!

Start by creating a file launch.py with the following lines

```python
from structools.launch import start

if __name__ == "__main__":

    start()
```

Then open the terminal in the folder where the file launch.py is located and simply run the following command

```bash
$ streamlit run launch.py
```

Welcome to Structools!

## Testing 

You can easily test that the package has been properly installed by creating a python file test.py (or any name you want) containing the following lines

```python
from structools.test import run_tests

if __name__ == "__main__":

    run_tests()
```

## Advanced/Further Development

For those willing to dive deeper into the code, please find below a brief way to generate your backtest:

```python
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
```


All the functionalities of the root package of this package are still available via the following command:

```python
import pybacktestchain
```

The relevant information about this pacakage is available here: https://pypi.org/project/pybacktestchain/

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`structools` was created by Romain Pifaut. It is licensed under the terms of the MIT license.

## Credits

`structools` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
