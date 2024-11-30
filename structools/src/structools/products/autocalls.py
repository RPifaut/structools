import numpy as np
import pandas as pd
from pydantic import BaseModel, validator, Field
from datetime import date
from typing import Union

from src.structools.tools.date_tools import DateModel
from src.structools.tools.date_tools import L_FREQ, DICT_MATCH_FREQ, find_dates_index
from src.structools.products.basic_products import Underlying


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
    recall_freq : str 
    first_trigger : float = Field(1.0, gt=0)
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

    @classmethod
    def from_params(cls, 
                    strike_date,
                    underlying,
                    maturity,
                    currency, 
                    start_recall, 
                    recall_freq,
                    first_trigger, 
                    step_down,
                    coupon,
                    coupon_trigger,
                    coupon_freq, 
                    is_memory,
                    call_strike,
                    call_leverage,
                    call_cap,
                    put_strike,
                    put_barrier, 
                    put_leverage,
                    put_barrier_observ,
                    kg):
        
        return cls(
            strike_date=strike_date, 
            underlying=underlying,
            maturity=maturity,
            currency=currency,
            first_trigger=first_trigger, 
            step_down=step_down,
            start_recall=start_recall,
            recall_freq=recall_freq, 
            coupon=coupon, 
            coupon_trigger=coupon_trigger, 
            coupon_freq=coupon_freq,
            is_memory=is_memory,
            call_strike=call_strike,
            call_leverage=call_leverage,
            call_cap=call_cap,
            put_strike=put_strike,
            put_barrier=put_barrier,
            put_leverage=put_leverage,
            put_barrier_observ=put_barrier_observ,
            kg=kg
        )
    

class Athena(Autocall):

    @classmethod
    def from_params(cls, 
                    strike_date,
                    underlying,
                    maturity,
                    currency, 
                    start_recall, 
                    recall_freq,
                    first_trigger, 
                    step_down,
                    coupon,
                    coupon_trigger,
                    coupon_freq, 
                    is_memory,
                    call_strike,
                    call_leverage,
                    call_cap,
                    put_strike,
                    put_barrier, 
                    put_leverage,
                    put_barrier_observ,
                    kg):
        
        return cls(
            strike_date=strike_date, 
            underlying=underlying,
            maturity=maturity,
            currency=currency,
            first_trigger=first_trigger, 
            step_down=step_down,
            start_recall=start_recall,
            recall_freq=recall_freq, 
            coupon=coupon, 
            coupon_trigger=coupon_trigger, 
            coupon_freq=coupon_freq,
            is_memory=is_memory,
            call_strike=call_strike,
            call_leverage=call_leverage,
            call_cap=call_cap,
            put_strike=put_strike,
            put_barrier=put_barrier,
            put_leverage=put_leverage,
            put_barrier_observ=put_barrier_observ,
            kg=kg
        )