import numpy as np
import pandas as pd
from pydantic import BaseModel, validator, Field
from tools.date_tools import DateModel, validator
from datetime import date
from tools.date_tools import L_FREQ, DICT_MATCH_FREQ, find_dates_index
from basic_products import Underlying
from typing import Union


# List with the possible type of observation for the put
L_OBS_PUT = ["European", "American"]


# ------------------------------------------------------------------------------------
# Useful functions
# ------------------------------------------------------------------------------------

def build_trigger_array(init_val : float = 1.0, step_down : float = 0.0, first_recall : int = 1, size : float = 10) -> np.ndarray:

    """
    Tool function to generate an array of triggers
    
    Parameters:

        init_val: First trigger value, expressed as a percentage of the strike price. Default is 1.0.
        step_down: Constant stepdown value, expressed in percentage. Default is 0.0.
        first_recall: Period from which we start observing the trigger. Default is 1.
        size: Size of the output array. Default is 10.

    Returns:
    
        trigger_array: Array containing the triggers, expressed in percentage of the strike price.
    """

    if first_recall < 0:
        raise ValueError(f"First recall cannot be negative. Got {first_recall}.")
    

    return np.array([999 if i < first_recall else init_val - step_down * (i - first_recall) for i in range(size)])





# ------------------------------------------------------------------------------------
# Autocall Classes
# ------------------------------------------------------------------------------------

class Autocall(BaseModel):

    """
    General class for the modeling of autocallablestructures. Please note that 

    - The product's maturity is expressed annually.
    - The values of the products's thresholds are expressed in fraction of the strike price.
    - The Coupon value must be exressed in annual terms.

    """

    # General features for all autocallable products
    strike_date : DateModel
    underlying : Union[Underlying, None]
    matu : float
    currency : Union[str, None]
    
    # Recall features
    start_recall : int = Field(1, gt=0)
    recall_freq : int = Field(1, gt=0)
    recall_trigger : float = Field(1.0, gt=0)
    step_down : float = Field(0.0, ge=0)


    # Coupon features
    coupon : float = Field(ge=0)
    coupon_trigger : float = Field(ge=0)
    coupon_freq : int = Field(ge=0)
    is_memory : bool

    # Participation upon recall
    call_strike : float = Field(1.0, ge=0)
    call_leverage : float = Field(0.0, ge=0)
    call_cap : float = Field(0.0, ge=0)

    # Put features
    put_strike : float = Field(1.0, ge=0)
    put_barrier : float = Field(0.7, ge=0)
    put_leverage : float = Field(0.0, ge=0)
    put_barrier_observ : str
    kg : float = Field(0.0, ge=0)



class Phoenix(Autocall):

    """
    This class represents a Phoenix Autocallable structure. 
    """

    def __init__(self, underlying : Underlying, maturity : float = None, currency : str = None, strike_date : date = None,
                 first_trigger : float = 1.0, step_down : float = 0.0, start_recall : int = 1, recall_freq : str = "A",
                 coupon : float = 0.05, first_coupon_trigger : float = 0.8, step_down_coupon : float = 0.0, 
                 start_coupon: int = 1, coupon_freq : str =  "A", is_memory : bool = True,
                 call_strike : float =  1.0, call_leverage : float = 0.0, call_cap : float = 1.05,
                 put_strike : float = 1.0, put_barrier : float = 0.7, put_leverage : float = 0.0, 
                 put_barrier_observ : str = "European", kg : float = 0.0):
        

        """
        Default constructor for phoenix classes

        Parameters
        
            underlying: Underlying asset.
            maturity: Maturity of the product expressed in years.
            currency: Currency in which the product is denomiated.
            strike_date: Strike date of the product.

            first_trigger: First trigger barrier level. Default is 1.0.
            step_down: Trigger step, expressed in %. Default is 0.0.
            start_recall: Period from which we shall start recalling. Default is 1.
            recall_frequency: Recall frequency. Default is "A" (annual).

            coupon: Coupon payment per observation. Default is 0.05
            first_coupon_trigger: First level for the coupon trigger. Default is 0.8.
            step_down_coupon: Trigger step for the coupon trigger, expressed in %. Default is 0.0.
            start_coupon: First coupon payment. Default is 1.
            coupon_freq: Coupon payment frequency. Expressed as a number of periodic payments per year. Default is 1.
            is_memory: Boolean for the memory effect on the Phoenix structure

            call_strike: Strike price for the call expressed in % of the strike price. Default is 1.
            call_leverage: Leverage on the call, expressed in %. Default is 0.
            call_cap: Maximum performance to be monetised on the upside, expressed in performance of the underlying. Default is 1.05.

            put_strike: Strike price for the downside protection, expressed in % of the strike price. Default is 1.
            put_barrier: Barrier level for the downside protection activation, expressed in % of the strike price. Default is 0.7.
            put_leverage: Leverage on the downside protection, expressed in percentage. Default is 0.0.
            put_barrier_observ: Observation type for the barrier, either European or American (close-to-close).
            kg: Percentage of capital guarantee on the product, expressed in % of the nominal. Default is 0.0.
        """

        # For each element, check the validity of the type and values
        if not isinstance(strike_date, date):
            TypeError(f"Expected type {date.__name__}.Got {type(strike_date).__name__}")
        else:
            self.strike_date = strike_date
        

        if not isinstance(underlying, Underlying):
            raise TypeError(f"Expected object of type Underlying. Got {type(underlying)}.")
        else:
            self.underlying = underlying


        if maturity < 0:
            raise ValueError(f"Maturity cannot be negative")
        elif maturity > 10:
            raise ValueError(f"Maximal maturity allowed for pricing is 10Y. Got {maturity}Y.")
        else:
            self.maturity = maturity


        self.currency = currency


        if not isinstance(start_recall, int):
            raise TypeError(f"Expected integer value. Got {type(start_recall).__name__}.")
        elif start_recall < 0:
            raise ValueError(f"Start Recall cannot be negative. Got {start_recall}.")
        else:
            self.start_recall = start_recall


        # Generate the recall triggers array
        if recall_freq not in L_FREQ:
            raise ValueError(f"Value {recall_freq} not supported. Possible values: {L_FREQ}")
        else:
            # Compute the number of observations to be considered for the product and generate the array of recall triggers
            n_obs = DICT_MATCH_FREQ[recall_freq]
            self.recall_trigger = build_trigger_array(first_trigger, step_down, start_recall, maturity * n_obs)    


        if coupon < 0:
            raise ValueError(f"Coupon value cannot be negative. Got {coupon}.")
        else:
            self.coupon = coupon

        
        if not isinstance(start_coupon, int):
            raise TypeError(f"Expected type int. got {type(start_coupon).__name__}")
        else:
            self.start_coupon = start_coupon
        
    
        # Generate the coupon trigger array
        if coupon_freq not in L_FREQ:
            raise ValueError(f"Value {coupon_freq} not supported. Possible values: {L_FREQ}")
        else:
            # Get the number of observations previously computed and generate the array of coupon triggers
            self.coupon_trigger = build_trigger_array(first_coupon_trigger, step_down_coupon, start_coupon, n_obs)

        
        self.is_memory = is_memory


        if call_strike < 0:
            raise ValueError(f"Strike Price for the call cannot be negative. Got {call_strike}.")
        else:
            self.call_strike = call_strike

        
        if call_leverage < 0:
            raise ValueError(f"Leverage for the call cannot be negative. Got {call_leverage}.")
        else:
            self.call_leverage = call_leverage
        

        if call_cap < 0:
            raise ValueError(f"Cap value for the call cannot be negative. Got {call_cap}")
        else:
            self.call_cap = call_cap
        

        if put_strike < 0:
            raise ValueError(f"Strike price for the put cannot be negative. Got {put_strike}.")
        else:
            self.put_strike =  put_strike

        
        if put_barrier < 0:
            raise ValueError(f"Put barrier cannot be negative. Got {put_barrier}.")
        else:
            self.put_barrier = put_barrier
        

        if put_leverage < 0:
            raise ValueError(f"Put leverage cannot be negative. Got {put_leverage}.")
        else:
            self.put_leverage = put_leverage
        

        if put_barrier_observ not in L_OBS_PUT:
            raise ValueError(f"{put_barrier_observ} not supported. Possible values: {L_OBS_PUT}")
        else:
            self.put_barrier_observ = put_barrier_observ

        
        if kg < 0:
            raise ValueError(f"Capital Guaranteed must be non-negative. Got {kg}.")
        else:
            self.kg = kg

