import logging
import pandas as pd
import numpy as np
from datetime import datetime as dt

from typing import List, Union, ClassVar
from pydantic import BaseModel, Field
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton

from structools.tools.market import Market, ACT
from structools.tools.date_tools import DateModel, find_dates_index, DICT_MATCH_FREQ
from structools.tools.timer import timer
from structools.products.autocalls import Autocall, Phoenix, Athena
from structools.products.basic_products import Underlying


logging.basicConfig(level=logging.INFO)

# Default objects
default_market = Market(data=dict())
VOID = -999

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
        [(date - arr_dates[0]).astype(int) / ACT for date in arr_dates]
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

    # Making sure all the index are valid
    if any(idx_dates >= df_underlying.index.shape[0]):
        logging.info(f"Missing data due to dates in the future. Disregarding the simulation starting on: {start_date}")
        return np.array([VOID for i in range(n_obs+1)]), np.array([DateModel(date=start_date).date for i in range(n_obs+1)]), VOID, VOID
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

@timer
def display_results(df_track : pd.DataFrame, arr_cf : np.ndarray, arr_idx_recall : np.ndarray, 
                    arr_ind_pdi : np.ndarray, mat_dates : np.ndarray) -> dict:

    """
    Function to present the results of the backtest

    Parameters:

        - df_track (pd.DataFrame): DataFrame containing the track of the underlying during the backtest.
        - arr_cf (np.ndarray): Matrix containing the cashflows related to each trajectory.
        - arr_idx_recall (np.ndarray): Array containing the indices of the periods at which an autocall event occurred, if any.
        - arr_ind_pdi (np.ndarray): Array containing the indicators about the occurrence of a barrier hit event.
        - mat_dates (np.ndarray): Matrix containing the observation date of each simulation.

    Return:

        - dict_res (dict): Dictionary containing the results of the backtest.

    """

    # Global variables
    N = arr_idx_recall.shape[0]
    dict_res = {}
    dict_res.update({"Number of trajectories": N})
    dict_res.update({"Underlying Track": df_track})

    # Compute metrics regarding the Autocall events
    arr_recall_periods = np.zeros((2, mat_dates.shape[1]-1))
    arr_recall_periods[0, :] = np.arange(mat_dates.shape[1]-1, dtype=int)
    for i in arr_recall_periods[0, :]:
        arr_recall_periods[1, int(i)] = sum(arr_idx_recall == int(i))
    arr_recall_periods[1, :] = arr_recall_periods[1, :] / N
    arr_recall_periods[0, :] += 1
    dict_res.update({"Recall Probabilities": arr_recall_periods})

    proba_autocall = arr_recall_periods[1, :-1].sum()
    dict_res.update({"Autocall Proba": proba_autocall})

    # Compute metrics related to the PDI
    proba_hit = sum(arr_ind_pdi) / N
    dict_res.update({"PDI Activation Proba": proba_hit})

    # IRR Computations
    arr_irr = np.zeros(N)
    arr_cf = np.hstack((np.ones((N, 1)) * (-1), arr_cf))
    for i in range(N):
        logging.info(f"Computing IRR for {int(i)}-th simulation")
        idx = arr_idx_recall[i]
        arr_cashflows = arr_cf[i][:int(idx)+2]
        arr_irr[i] = compute_irr(arr_cashflows, mat_dates[i, :int(idx)+2])
    
    # IRR Statistics
    dict_irr_stats={
        "Average": arr_irr.mean(),
        "25% Percentile": np.percentile(arr_irr, 25),
        "Median": np.percentile(arr_irr, 50), 
        "75% Percentile": np.percentile(arr_irr, 75)
    }

    dict_res.update({"IRR Stats": dict_irr_stats})

    return dict_res



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
        arr_return = np.ones(arr_recall.shape[0]) * (VOID)
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



# ----------------------------------------------------------------------------------
# Backtester Class 
# ----------------------------------------------------------------------------------


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
                        investment_horizon):
        
        """
        Default method to create a backtester instance
        """

        # Generate the market
        end_date = dt.today()
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
   
    @timer
    def backtest_autocall(self) -> dict:

        """
        Main method to run a backtest for a specific product.

        Returns:

            - dict_res (dict): Dictionary containing the backtest results

        """

        # Definition and assignment of the backtest variables
        prod = self.product
        undl = prod.underlying
        NOBS = prod.arr_recall_trigger.shape[0]
        logging.info(f"Number of observations: {NOBS}.")

        # Feature matrix
        mat_feat = np.zeros((prod.arr_recall_trigger.shape[0], 3))
        mat_feat[:, 0] = prod.arr_recall_trigger
        mat_feat[:, 1] = prod.arr_coupon_trigger
        mat_feat[:, 2] = prod.arr_coupons

        # Upside participation features array
        arr_call = np.array(
            [
                prod.call_strike,
                prod.call_leverage,
                prod.call_cap
            ]
        )
        
        # Downside protection features array
        arr_put = np.array(
            [
                prod.put_strike,
                prod.put_barrier,
                prod.put_leverage,
                prod.kg
            ]
        )

        # Dates
        END = dt.today()
        START = END - relativedelta(years=self.investment_horizon + self.backtest_length)

        # Build track of the underlying
        df_ret = undl.compute_return_compo(DateModel(date=START),
                                           DateModel(date=END),
                                           True,
                                           market=self.market
                                           )
        
        df_track = undl.build_track(DateModel(date=START),
                                    DateModel(date=END),
                                    df_ret
                                    )[undl.name]
        
        # Retrieve the observation values
        idx_last_date = np.searchsorted(df_track.index, END - relativedelta(years=self.investment_horizon))
        arr_start_dates = df_track.index[:idx_last_date]
        logging.info(f"Last Starting Date: {arr_start_dates[-1]}")
        NSIM = arr_start_dates.shape[0]
        mat_obs, mat_dates, arr_min_val, arr_min_date = get_all_observations(arr_start_dates,
                                                                             NOBS,
                                                                             prod.recall_freq,
                                                                             df_track)
        

        # Removing the starting dates for which we do not have enough data
        mat_obs = np.delete(mat_obs, np.where(mat_obs[:, 0] == VOID)[0], axis=0)

        # Removing the first observation (strike date) from the mat_obs
        mat_obs_perf = mat_obs[:, 1:]

        # Running the backtest
        arr_cf = np.zeros((NSIM, NOBS))
        arr_idx_recall = np.zeros(NSIM)
        arr_ind_pdi = np.zeros(NSIM)
        arr_cf, arr_idx_recall, arr_ind_pdi = all_paths_backtest(mat_feat, 
                                                                 arr_call,
                                                                 arr_put, 
                                                                 prod.is_memory,
                                                                 arr_min_val, 
                                                                 prod.put_barrier_observ,
                                                                 mat_obs_perf)
        
        # Preparing the results
        dict_res = display_results(df_track,
                                   arr_cf,
                                   arr_idx_recall,
                                   arr_ind_pdi,
                                   mat_dates)  
        dict_res.update({"Product": prod})
        dict_data = {
            "Observations": mat_obs,
            "Dates": mat_dates,
            "Cashflows": arr_cf
        }
        dict_res.update({"Data": dict_data})
        logging.info("Backtest completed!")
        return dict_res      