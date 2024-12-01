import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from typing import List
from src.structools.tools.date_tools import DateModel
from pybacktestchain.data_module import DataModule, get_stocks_data



# ---------------------------------------------------------------------
# General Functions
# ---------------------------------------------------------------------

def load_stocks_data(tickers : List[str], start_date : DateModel, end_date : DateModel) -> pd.DataFrame:

    """
    This function is used to generated standardised output for Equity market data. It is based on pybacktestchain's get_stocks_data function.

    Parameters:

        tickers (List[str]): List of tickers you want to load data from
        start_date (DateModel): Date from which we start loading data
        end_date (DateModel): Date at which we stop loading data

    Returns:

        pd.DataFrame: Pandas DataFrame with the historical data

    """

    # Get the data from the original function
    df_output = get_stocks_data(tickers, start_date.to_str(), end_date.to_str()).set_index("Date")

    # Convert the index types so it is compatible with the rest of the package
    df_output.index = pd.DatetimeIndex(
        list(
            map(
                lambda date: DateModel(date=date).date, df_output.index.values
            )
        )
    )

    return df_output
