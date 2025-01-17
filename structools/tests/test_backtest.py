import pytest
import copy
import numpy as np
import pandas as pd
from pydantic import ValidationError
import plotly.graph_objects as go

from tests.params import *
from structools.tools.market import Market
from structools.products.autocalls import Autocall, Athena, Phoenix
from structools.products.basic_products import Underlying, Basket
from structools.backtest.backtester import Backtester

def test_backtester():

    # Default Underlying


    # Backtesting Athena - Phoenix
    dict_athena = DICT_ATHENA.copy()
    dict_athena["underlying"] = BASKET
    athena = Athena.from_params(**dict_athena)
    bt_athena = Backtester.init_backtester(product=athena, backtest_length=10, 
                                            investment_horizon=athena.maturity)
    dict_phoenix = DICT_PHOENIX.copy()
    dict_phoenix["maturity"] = 5
    dict_phoenix["underlying"] = BASKET
    phoenix = Phoenix.from_params(**dict_phoenix)
    bt_phoenix = Backtester.init_backtester(product=phoenix, backtest_length=10, 
                                            investment_horizon=phoenix.maturity)
    
    # Assert correct instantiation
    assert isinstance(bt_athena, Backtester)
    assert isinstance(bt_phoenix, Backtester)

    # Assert correct results
    res_athena = bt_athena.backtest_autocall()
    res_phoenix = bt_phoenix.backtest_autocall()

    assert isinstance(res_athena, dict)
    assert isinstance(res_phoenix, dict)
    assert res_athena["Recall Probabilities"].shape[1] == 120
    assert res_phoenix["Recall Probabilities"].shape[1] == 60
    assert isinstance(res_athena["Underlying Track"], pd.Series)


