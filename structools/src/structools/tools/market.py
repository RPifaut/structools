import pandas as pd
import numpy as np
import logging
from pydantic import BaseModel, Field
from typing import List, Dict
from structools.tools.date_tools import DateModel
from pybacktestchain.data_module import DataModule, get_stocks_data

logging.basicConfig(level=logging.INFO)

L_PRICES = ["Open", "High", "Low", "Close", "Adj. Close"]
ACT = 365



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
    df_output.index = pd.Index(
        list(
            map(
                lambda d: DateModel(date=d).date,
                df_output.index.values
            )
        )
    )



    return df_output


class Market(BaseModel):

    """
    This class will be used for the backtest of strategies. It aims at preventing the use of out of sample date in estimations.
    """

    class Config:

        arbitrary_types_allowed = True

    data : Dict[str, pd.DataFrame]


    @classmethod
    def create_market(cls, tickers : List[str], start_date : DateModel, end_date : DateModel, uniform : bool = True):

        """
        Class method to create an instance of market.

        Parameters:

            tickers (List[str]): List of the tickers of companies composing the market
            start_date (DateModel): Date from which we start loading the data
            end_date (DateModel): Date at which we stop loading the data
            uniform (bool): Boolean to indicate whether we only keep days where there is quotation for all components. Default is True

        Returns:

            Instance of market

        """

        dict_data = {}

        # Load the market data
        logging.info("Start loading market data.")
        df_data = load_stocks_data(tickers, start_date, end_date)
        logging.info("Data loading completed.")
        
        # Break the output down by ticker and store them in the dictionary
        for ticker in tickers:
            dict_data.update(
                {
                    ticker: df_data[df_data["ticker"]==ticker]
                }
            )

        # If set to True, create a uniform index
        if uniform:
            
            # Create Uniform index
            logging.info("Homogenising the data with respect to the dates.")
            my_index = df_data[df_data["ticker"]==tickers[0]].index
            for ticker in tickers:
                my_index = np.intersect1d(my_index, dict_data[ticker].index)

            # Modify
            my_index = pd.DataFrame(index = my_index)
            for ticker in tickers:
                dict_data[ticker] = pd.concat([my_index, dict_data[ticker]], axis=1, join='inner')

        logging.info("Market sucessfully created.")

        return cls(data = dict_data)