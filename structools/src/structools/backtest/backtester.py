import logging
import pandas as pd
import numpy as np
from datetime import datetime as dt

from typing import List, Union, ClassVar
from pydantic import BaseModel, Field
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton
from numba import jit, prange

from src.structools.tools.market import Market, ACT
from src.structools.tools.date_tools import DateModel, find_dates_index, DICT_MATCH_FREQ
from src.structools.tools.timer import timer
from src.structools.products.autocalls import Autocall, Phoenix, Athena
from src.structools.products.basic_products import Underlying


logging.basicConfig(level=logging.INFO)

# Default objects
default_market = Market(data=dict())

# ----------------------------------------------------------------------------------
# Tool Functions 
# ----------------------------------------------------------------------------------

def compute_irr(arr_cashflows : np.ndarray, arr_dates : np.ndarray):

    """
    Function that computes the IRR of an investment. Handle non-linear spacing between payment dates

    Parameters:

        arr_cashflows (np.ndarray): Array containing the various cashflows
        arr_dates (np.ndarray): Array containing the associated payment dates

    Returns:

        irr (float): IRR of the investment
    """

    arr_time_since_incept = np.array(
        [(date - arr_dates[0]) / ACT for date in arr_dates]
    )
    # Tool function that computes the NPV of the investment
    def npv(irr):

        return sum(
            cf / (1+irr) ** t for cf, t in zip(arr_cashflows, arr_time_since_incept)
        ) 
    
    # IRR Computation, initial guess of 7% per annum
    try:
        irr = newton(npv, x0=0.07)
    except:
        irr = np.nan
        logging.info("IRR computation failed.")

    return irr


def get_observations_values(start_date : np.datetime64, n_obs : int, freq : str, df_underlying : pd.DataFrame) -> np.ndarray:

    """
    Function retrieving the values of the underlying's values on observations dates.

    Parameters:

        - start_date (np.datetime64): Date of the launch of the product.
        - n_obs (int): Number of observations.
        - freq (str): Observation Frequency.
        - df_underlying (pd.DataFrame): DataFrame containing the Underlying's performance.

    Returns:

        - (arr_obs_perf, arr_dates) (tup): Tuple containing arrays with the values on the observation dates and the observation dates.

    """

    # Find the important observation dates
    idx_dates = find_dates_index(start_date, n_obs, freq, df_underlying.index)
    arr_dates = np.r_[DateModel(date=start_date).date, df_underlying.index.values[idx_dates]]
    arr_obs_perf = np.r_[df_underlying[start_date], df_underlying.values[idx_dates]]
    arr_obs_perf = arr_obs_perf / arr_obs_perf[0]

    # Find the worst performance to know whether barrier hit and when
    df_temp = df_underlying.loc[start_date:arr_dates[-1]]
    min_val = df_temp.min()
    date_min = df_temp.idxmin()
    
    return arr_obs_perf, arr_dates, min_val, date_min


def get_all_observations(arr_start_dates : np.ndarray, n_obs : int, freq : str, df_underlying : pd.DataFrame) -> np.ndarray:

    """
    Function retrieving the values of the underlying's values on observations dates.

    Parameters:

        - arr_start_date (np.ndarray): Array of dates of the launch of the product.
        - n_obs (int): Number of observations.
        - freq (str): Observation Frequency.
        - df_underlying (pd.DataFrame): DataFrame containing the Underlying's performance.

    Returns:

        - (arr_obs_perf, arr_dates, arr_min_val, arr_min_dates) (tup): Tuple containing matrices with the values on the observation dates and the observation dates.

    """

    # Matrix containing the results
    logging.info("Retrieving observation dates and performances")
    mat_obs_perf = np.zeros((len(arr_start_dates), n_obs+1))
    mat_obs_dates = np.empty((len(arr_start_dates), n_obs+1), dtype="datetime64[D]")
    arr_min_val = np.zeros(len(arr_start_dates))
    arr_min_dates = np.empty(len(arr_start_dates), dtype="datetime64[D]")

    # Retrieving the arrays of values
    for i in range(len(arr_start_dates)):
        obs, dates, min_val, min_date = get_observations_values(arr_start_dates[i], n_obs, freq, df_underlying)
        mat_obs_perf[i, :], mat_obs_dates[i, :], arr_min_val[i], arr_min_dates[i] = obs, dates, min_val, min_date
    logging.info("Observation values successfully retrieved.")

    return mat_obs_perf, mat_obs_dates, arr_min_val, arr_min_dates




# ----------------------------------------------------------------------------------
# Backtest Functions 
# ----------------------------------------------------------------------------------

# @jit(nopython=True)
def mono_path_backtest(arr_feat : np.ndarray, arr_call : np.ndarray, arr_put : np.ndarray, memory : bool, 
                           min_val : float, put_obs : str, arr_obs : np.ndarray):

        """
        Function running a backtest on one given path.

        Parameters:

            - arr_feat (np.ndarray): Array containing the ordered necessary product features.
            - arr_call (np.ndarray): Array containing the call features for upside performance at maturity.
            - arr_put (np.ndarray): Array containing the put features for the downside protection at maturity.
            - memory (bool): Whether the product has memory coupons or not
            - min_val (float): Minimum value reached during the product's life.
            - put_obs (str): Put activation observation
            - arr_obs (np.ndarray): Array containing the observation values of the relevant observation dates.

        Returns:

            - arr_cashflow (np.ndarray): Array containing the cashflows of the simulation.
            - idx_recall (int): Index of the recall period if any.
            - ind_pdi (bool): Indicator of barrier hit.

        """

        # Default values
        ind_pdi = 0

        # Recall condition
        arr_recall = arr_obs >= arr_feat[:, 0]
        if np.any(arr_recall):
            idx_recall = np.argmax(arr_recall)
        else:
            idx_recall = arr_recall.shape[0] - 1

        # Output arrays
        arr_paid_coupon = np.zeros(idx_recall+1)
        arr_cashflows = np.zeros(idx_recall+1)

        # Coupon payment - immediately resized in case of autocall for performance effiency
        if idx_recall != arr_recall.shape[0] - 1:
            arr_coupon_trigger = arr_feat[:idx_recall+1, 1]
            arr_coupon = arr_feat[:idx_recall+1, 2]
        else:
            arr_coupon_trigger = arr_feat[:, 1]
            arr_coupon = arr_feat[:, 2]           

        if memory:
            # First Payment
            arr_paid_coupon[0] = arr_coupon[0] if arr_obs[0] >= arr_coupon_trigger[0] else 0

            # Other payments, if any
            if idx_recall > 0:
                for i in range(1, arr_coupon_trigger.shape[0]):
                    if arr_obs[i] >= arr_coupon_trigger[i]:
                        arr_paid_coupon[i] = sum(arr_coupon[:i]) - sum(arr_paid_coupon[:i-1])
                    else:
                        arr_paid_coupon[i] = 0

        else:
            for i in range(arr_coupon_trigger.shape[0]):
                if arr_obs[i] >= arr_coupon_trigger[i]:
                    arr_paid_coupon[i] = arr_coupon[i]
                else:
                    arr_paid_coupon[i] = 0

        # Pre combining the cashflows together
        arr_cashflows = arr_paid_coupon

        # Scenarii at maturity
        if idx_recall == arr_recall.shape[0] - 1:
            
            # (Capped) Upside Participation
            upside = arr_call[1] * min(max(arr_obs[-1] - arr_call[0], 0), arr_call[2])

            # Downside protection
            if put_obs == "AMERICAN":
                ind_pdi = min_val <= arr_put[1]
            else:
                ind_pdi = arr_obs[-1] <= arr_put[-1]
            
            pdi = ind_pdi * max(arr_put[0] - arr_put[2] * arr_obs[-1], 0)

            # Considering capital protection, and barrier activation
            capital = max(arr_put[3], 1 - pdi) * ind_pdi + (1-ind_pdi) * 1 

            # Adding the final performances if the product lives up until maturity
            arr_cashflows[-1] += upside + capital
        
        else:
            arr_cashflows[-1] += 1          # Capital added in case of recall

        # Adjusting the length of the cashflows
        arr_return = np.ones(arr_recall.shape[0]) * (-999)
        arr_return[:idx_recall+1] = arr_cashflows

        return arr_return, idx_recall, ind_pdi


@timer
def all_paths_backtest(arr_feat : np.ndarray, arr_call : np.ndarray, arr_put : np.ndarray, memory : bool, 
                           arr_min_val : np.ndarray, put_obs : str, mat_obs : np.ndarray):
    
        """
        Function running a backtest on all paths.

        Parameters:

            - arr_feat (np.ndarray): Array containing the ordered necessary product features.
            - arr_call (np.ndarray): Array containing the call features for upside performance at maturity.
            - arr_put (np.ndarray): Array containing the put features for the downside protection at maturity.
            - memory (bool): Whether the product has memory coupons or not
            - min_val (np.ndarray): Minimum value reached during the product's life.
            - put_obs (str): Put activation observation
            - mat_obs (np.ndarray): Matrices containing the observation values of the relevant observation dates.

        Returns:

            - arr_cashflow (np.ndarray): Array containing the cashflows of the simulation.
            - idx_recall (int): Index of the recall period if any.
            - ind_pdi (bool): Indicator of barrier hit.

        """

        # Output parameters
        NSIM = mat_obs.shape[0]
        NOBS = arr_feat.shape[0]
        arr_cf = np.zeros((NSIM, NOBS))                     # Array storing the cashflows related to each simulation
        arr_idx_recall = np.zeros(NSIM)                     # Array storing the recall index period
        arr_pdi = np.zeros(NSIM)                            # Array storing the indicators of downside protection activation

        # Looping on the dates
        for i in range(NSIM):
            arr_cf[i, :], arr_idx_recall[i], arr_pdi[i] = mono_path_backtest(
                arr_feat=arr_feat, 
                arr_call=arr_call,
                arr_put=arr_put, 
                memory=memory,
                min_val=arr_min_val[i],
                put_obs=put_obs,
                arr_obs=mat_obs[i,:]
            )

        return arr_cf, arr_idx_recall, arr_pdi


class Backtester(BaseModel):

    class Config:

        arbitrary_types_allowed = True

    product : Union[Autocall, Underlying]
    backtest_length : float = Field(10, gt=0)
    investment_horizon : int = Field(10, gt=0)
    market : Market = Field(default_market)

    # mono_path_backtest : ClassVar = None


    @classmethod
    def init_backtester(cls,
                        product,
                        backtest_length,
                        investment_horizon,
                        end_date):
        
        """
        Default method to create a backtester instance
        """

        # Generate the market
        end_date = pd.Timestamp(end_date).to_pydatetime()
        start_date = end_date - relativedelta(years=investment_horizon + backtest_length)
        market = Market.create_market(
            product.underlying.COMPO, 
            DateModel(date=start_date), 
            DateModel(date=end_date)
        )

        return cls(
            product=product,
            backtest_length=backtest_length,
            investment_horizon=investment_horizon,
            market=market
        )
    
    
    # ---------------------------------------------------------------------------------------
    # Backtester for the autocalls
    # ---------------------------------------------------------------------------------------
   







            



        
    
    # def backtest_autocall(self, price : str = 'Close') -> pd.DataFrame:

    #     """
    #     Method to backtest an autocall product.

    #     Parameters:

    #         price (str): Type of price to look at for the data loading

    #     Returns:

    #         df_backtest (pd.DataFrame): DataFrame containing the backtest results
            
    #     """

    #     UNDERLYING = self.product.underlying.COMPO
    #     END = dt.date.today()
    #     START = END - relativedelta(years=self.backtest_length + self.investment_horizon)

    #     # Get the underlying track
    #     df_perf = self.product.underlying.compute_return_compo(UNDERLYING, START, END)

    #     # General parameters
    #     last_idx = np.searchsorted(df_perf.index, END - relativedelta(years=self.investment_horizon))
    #     arr_start = df_perf.index[:last_idx]
    #     n_sim = len(arr_start)
    #     df_backtest = pd.DataFrame(
    #         index=arr_start,
    #     )

    #     arr_recall_period = np.zeros(n_sim)
    #     arr_autocalled = np.zeros(n_sim)
    #     arr_irr = np.zeros(n_sim)


    #     # Loop on the dates
    #     logging.info(f"Backtesting from {START} to {END} for a total of {n_sim} trajectories.")
    #     i = 0
    #     for date_init in arr_start:

    #         # Generate the data and temporary variables
    #         ind_recall = 0
    #         df_temp = df_perf.loc[date_init:date_init + relativedelta(years=self.investment_horizon)]
    #         df_temp = self.product.underlying.build_track(DateModel(date=df_temp.index[0]),
    #                                                       DateModel(date=df_temp.index[-1]),
    #                                                       df_temp)
            
    #         # Arrays of dates for observations
    #         arr_recall_idx = find_dates_index(DateModel(date=date_init).date,
    #                                       self.product.maturity * DICT_MATCH_FREQ[self.product.recall_freq],
    #                                       self.product.recall_freq,
    #                                       df_temp.index)
            
    #         arr_coupon_idx = find_dates_index(DateModel(date=date_init).date,
    #                                       self.product.product.maturity * DICT_MATCH_FREQ[self.product.coupon_freq],
    #                                       self.product.coupon_freq,
    #                                       df_temp.index)
            
    #         # Determine whether an autocall event has occurred
    #         arr_has_autocalled = pd.concat([pd.DataFrame(arr_recall_idx), df_temp], axis=1, join='inner')
    #         arr_has_autocalled = arr_has_autocalled[self.product.underlying.name] >= self.product.arr_recall_trigger
            
    #         if not any(arr_has_autocalled):
    #             # Case no autocall
    #             ind_recall = 0
    #             logging.info(f"Trajectory {i}, started on {date_init} did not autocall.")
                
    #         else:
    #             recall_period = np.argmax(arr_has_autocalled)
    #             recall_date = df_temp.index[recall_period]

    #         # Determine the coupons that can be paid (exluding the occurrences after the recall for computation efficiency)
    #         df_coupon = pd.concat([pd.DataFrame(index=arr_coupon_idx), df_temp], axis=1, join='inner')
    #         if ind_recall == 1:
    #             df_coupon = df_coupon.loc[:recall_date]
    #         arr_coupon_paid = df_coupon[self.product.underlying.name] >= self.product.arr_coupon_trigger
    #         arr_coupon_paid = arr_coupon_paid * self.product.coupon

    #         if self.product.is_memory:
    #             arr_all_coupon_paid = np.ones(len(arr_coupon_paid)) * self.product.coupon
    #             arr_all_coupon_paid = arr_all_coupon_paid.cumsum()
    #             arr_cum_coupon = arr_coupon_paid.cumsum()
    #             arr_cum_coupon = np.r_[0, arr_all_coupon_paid[:-1]]
    #             arr_coupon_paid = arr_all_coupon_paid - arr_cum_coupon

    #         # Scenario at maturity if no autocall
    #         if ind_recall == 0:

    #             # Check for positive performance
    #             call_perf = self.product.call_leverage * np.min(
    #                 np.max(
    #                     df_perf.iloc[-1, 0] - self.call_strike, 0
    #                 ), self.call_cap
    #             )

    #             # Check if PDI has been activate, considering the capital guarantee
    #             if self.product.put_barrier_observ == "EUROPEAN":
    #                 activated = df_perf.iloc[-1, 0] <= self.product.put_barrier
    #             else:
    #                 activated = any(df_perf[self.product.underlying.name] <= self.product.put_barrier)

    #             if activated:
    #                 logging.INFO(f"Trajectory {i}, started on {date_init}, trigger a barrier event.")

    #             pdi_loss = np.min(
    #                 activated * self.product.put_leverage * np.max(
    #                     self.product.put_strike - df_temp.iloc[-1, 0], 0
    #                 ), 1 - self.product.kg
    #             )

    #             payoff_matu = 1 + call_perf - pdi_loss
    #             arr_coupon_paid[-1] += payoff_matu

    #         # Compute IRR
    #         s_recall = pd.Series(np.zeros(len(arr_has_autocalled)), index=arr_coupon_idx)
    #         s_coupons = pd.Series(np.zeros(len(arr_coupon_paid)), index=arr_coupon_idx)

    #         if ind_recall:
    #             s_recall=s_recall.loc[:recall_date]
    #             s_recall[-1] = 1
    #             s_coupons=s_coupons.loc[:recall_date]
    #         df_temp = pd.concat([s_recall, s_coupons], axis=1)
    #         arr_cashflows = df_temp.sum(axis=1)
    #         arr_dates = df_temp.index
    #         irr = compute_irr(arr_cashflows, arr_dates)

    #         # Store the results
    #         arr_autocalled[i]=ind_recall
    #         arr_recall_period[i]=recall_period if ind_recall else 0
    #         arr_irr[i]=irr

    #         i+=1

    #     # Prepare the output DataFrame
    #     logging.info("Backtest completed!")
    #     df_backtest = pd.DataFrame(
    #         data=[arr_autocalled, arr_recall_period, arr_irr],
    #         index=["Has Autocalled", "Autocall Period", "IRR"],
    #         columns = [f"Simulation {i}" for i in range(len(arr_start))]
    #     )

    #     return df_backtest


