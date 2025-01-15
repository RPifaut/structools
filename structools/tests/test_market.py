import pytest

from src.structools.tools.market import Market, load_stocks_data
from src.structools.tools.date_tools import DateModel
from tests.params import *

def test_data_loading():

    df_data = load_stocks_data(tickers=L_COMPO, start_date=DateModel(date="2001-10-22"), end_date=DateModel(date="2024-10-22"))

    assert len(set(df_data["ticker"])) == len(L_COMPO)
    assert df_data.shape[0] == 23250

def test_market_creation():

    market = Market.create_market(tickers=L_COMPO, start_date=START_DATE, end_date=END_DATE, uniform=True)

    assert len(market.data.keys()) == len(L_COMPO)