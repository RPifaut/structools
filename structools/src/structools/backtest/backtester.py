import logging
import pandas as pd
import numpy as np
import datetime as dt
from typing import List, Union
from pydantic import BaseModel, Field
from dateutil.relativedelta import relativedelta

from src.structools.tools.market import Market
from src.structools.tools.date_tools import DateModel, find_dates_index, DICT_MATCH_FREQ
from src.structools.products.autocalls import Autocall, Phoenix, Athena
from src.structools.products.basic_products import Underlying



logging.basicConfig(level=logging.INFO)


class Backtester(BaseModel):

    class Config:

        arbitrary_types_allowed = True

    product : Union[Autocall, Underlying]
    backtest_length : float = Field(10, gt=0)
    investment_horizon : int = Field(10, gt=0)


    @classmethod
    def init_backtester(cls,
                        product,
                        backtest_length,
                        investment_horizon,
                        tickers,
                        end_date):
        
        """
        Default method to create a backtester instance
        """

        # Generate the market
        market = Market.create_market(
            tickers, 
            DateModel(date=end_date).date - relativedelta(years=investment_horizon), 
            DateModel(end_date).date
        )

        return cls(
            product=product,
            backtest_length=backtest_length,
            investment_horizon=investment_horizon,
        )
    
    
    # ---------------------------------------------------------------------------------------
    # Backtester for the autocalls
    # ---------------------------------------------------------------------------------------

    def backtest_autocall(self, price : str = 'Close') -> pd.DataFrame:

        """
        Method to backtest an autocall product.

        Parameters:

            price (str): Type of price to look at for the data loading

        Returns:

            df_backtest (pd.DataFrame): DataFrame containing the backtest results
            
        """

        UNDERLYING = self.product.underlying.COMPO
        END = dt.date.today()
        START = END - relativedelta(years=self.backtest_length + self.investment_horizon)

        # Get the underlying track
        df_perf = self.product.underlying.compute_return_compo(UNDERLYING, START, END)

        # General parameters
        last_idx = np.searchsorted(df_perf.index, END - relativedelta(years=self.investment_horizon))
        arr_start = df_perf.index[:last_idx]
        n_sim = len(arr_start)
        df_backtest = pd.DataFrame(
            index=arr_start,
        )

        arr_recall_periods = np.zeros(n_sim)
        arr_irr = np.zeros(n_sim)


        # Loop on the 
        for date_init in arr_start:

            # Generate the data and temporary variables
            ind_recall = 0
            df_temp = df_perf.loc[date_init:date_init + relativedelta(years=self.investment_horizon)]
            df_temp = self.product.underlying.build_track(DateModel(date=df_temp.index[0]),
                                                          DateModel(date=df_temp.index[-1]),
                                                          df_temp)
            
            # Arrays of dates for observations
            arr_recall_idx = find_dates_index(DateModel(date=date_init).date,
                                          self.product.maturity * DICT_MATCH_FREQ[self.product.recall_freq],
                                          self.product.recall_freq,
                                          df_temp.index)
            
            arr_coupon_idx = find_dates_index(DateModel(date=date_init).date,
                                          self.product.product.maturity * DICT_MATCH_FREQ[self.product.coupon_freq],
                                          self.product.coupon_freq,
                                          df_temp.index)
            
            # Determine whether an autocall event has occurred
            arr_has_autocalled = pd.concat([pd.DataFrame(arr_recall_idx), df_temp], axis=1, join='inner')
            arr_has_autocalled = arr_has_autocalled[self.product.underlying.name] >= self.product.arr_recall_trigger

            if not any(arr_has_autocalled):
                # Case no autocall
                ind_autocall = 0
            else:
                recall_period = np.argmax(arr_has_autocalled)
                recall_date = df_temp.index[recall_period]

            # Determine the coupons that can be paid (exluding the occurrences after the recall for computation efficiency)
            df_coupon = pd.concat([pd.DataFrame(index=arr_coupon_idx), df_temp], axis=1, join='inner')
            arr_coupon_paid = df_coupon[self.product.underlying.name] >= self.product.arr_coupon_trigger

            # Scenario at maturity if no autocall
            if ind_autocall == 0:

                # Check for positive performance
                call_perf = self.product.call_leverage * np.min(
                    np.max(
                        df_perf.iloc[-1, 0] - self.call_strike, 0
                    ), self.call_cap
                )

                # Check if PDI has been activate, considering the capital guarantee
                if self.product.put_barrier_observ == "EUROPEAN":
                    activated = df_perf.iloc[-1, 0] <= self.product.put_barrier
                else:
                    activate = any(df_perf[self.product.underlying.name] <= self.product.put_barrier)

                pdi_loss = np.min(
                    activated * self.product.put_leverage * np.max(
                        self.product.put_strike - df_temp.iloc[-1, 0], 0
                    ), 1 - self.product.kg
                )
