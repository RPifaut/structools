import numpy as np
import pandas as pd
from pydantic import BaseModel, field_validator, Field
from datetime import date
from typing import Union, Literal

from structools.tools.date_tools import DateModel
from structools.tools.date_tools import L_FREQ, DICT_MATCH_FREQ, find_dates_index
from structools.products.basic_products import Underlying

import logging
logging.basicConfig(level=logging.INFO)

# List with the possible type of observation for the put
L_OBS_PUT = ["EUROPEAN", "AMERICAN"]
L_CCY = ["EUR", "USD", "GBP", "CHF", "CHF", "SEK", "NOK", "AUD"]

# Default objects

default_underlying  = Underlying()


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
    
    start = first_recall - 1
    return np.array([999 if i < start else init_val - step_down * (i - start) for i in range(size)])





# ------------------------------------------------------------------------------------
# Autocall Classes
# ------------------------------------------------------------------------------------

class Autocall(BaseModel):

    class Config:
        
        arbitrary_types_allowed = True      # Allow the template to use inputs with types different from Python default types
        extra = "forbid"                    # Forbid the creation of extra fields in child classes
        frozen = False                      # Allow for mutations using setters


    # General features for all autocallable products
    strike_date : DateModel = Field (DateModel(date="2001-10-22"))
    underlying : Underlying = Field(default_underlying)
    maturity : int = Field(10, ge=1)
    currency : str = Field("EUR")
    
    # Recall features
    start_recall : int = Field(1, gt=0)
    recall_freq : str = "A"
    first_trigger : float = Field(1.0, gt=0)
    step_down : float = Field(0.0, ge=0)


    # Coupon features
    coupon : float = Field(0.05, ge=0)
    coupon_trigger : float = Field(0.8, gt=0)
    start_coupon : int = Field(1, ge=0)
    is_memory : bool = False

    # Participation upon recall
    call_strike : float = Field(1.0, ge=0)
    call_leverage : float = Field(0.0, ge=0)
    call_cap : float = Field(0.0, ge=0)

    # Put features
    put_strike : float = Field(1.0, ge=0)
    put_barrier : float = Field(0.7, ge=0)
    put_leverage : float = Field(0.0, ge=0)
    put_barrier_observ : str = "EUROPEAN"
    kg : float = Field(0.0, ge=0)


    # Arrays of data for backtests
    arr_recall_trigger : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array containing all the values of the recall triggers."
    )

    arr_recall_dates : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description = "Array containing the dates to be matched for the autocall condition."
    )

    arr_coupon_trigger : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array containing the values of the coupon trigger."
    )

    arr_coupon_dates : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array containing the dates to be matched for the coupon condition."
    )

    arr_coupons: np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array containing the values of the coupon at each date."
    )

    arr_put_observ : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array containing the dates on which we shall observe the barrier for the put"
    )

    # Data Validators for the frequency types
    @field_validator("recall_freq", mode="before")
    def recall_freq_validation(cls, value):

        if value not in L_FREQ:
            raise ValueError(f"Frequency {value} not supported. Only accepts: {L_FREQ}.")

        return value


    # --------------------------------------------------------------------
    # Common Methods to all Autocalls
    # --------------------------------------------------------------------

    def set_parameter(self, attribute_name : str, value):

        if attribute_name not in self.model_fields:
            raise AttributeError(f"Impossible to create or change the value of attribute {attribute_name}.")
        
        if not isinstance(value, type(getattr(self, attribute_name))):
            raise TypeError(f"Expected {type(getattr(self, attribute_name)).__name__}. Got {type(value).__name__}")
        
        setattr(self, attribute_name, value)


    def get_parameter(self, attribute_name : str):

        if attribute_name not in self.model_fields:
            raise AttributeError(f"Cannot return a value for attribute {attribute_name} as it is not a class attribute of the Phoenix object.")
        else:
            return getattr(self, attribute_name)

    



class Phoenix(Autocall):

    """
    Default class method to create an instance of an Athena product.
    """

    @classmethod                # Allows to instantiate an object using default values when missing arguments
    def from_params(cls, 
                strike_date: DateModel = Autocall.model_fields['strike_date'].default,
                underlying: Underlying = Autocall.model_fields['underlying'].default,
                maturity: int = Autocall.model_fields['maturity'].default, 
                currency: str = Autocall.model_fields['currency'].default,
                start_recall: int = Autocall.model_fields['start_recall'].default, 
                recall_freq: str = Autocall.model_fields['recall_freq'].default, 
                first_trigger: float = Autocall.model_fields['first_trigger'].default,
                step_down: float = Autocall.model_fields['step_down'].default, 
                coupon: float = Autocall.model_fields['coupon'].default,
                coupon_trigger: float = Autocall.model_fields['coupon_trigger'].default,
                start_coupon: int = Autocall.model_fields['start_coupon'].default, 
                is_memory: bool = Autocall.model_fields['is_memory'].default,
                call_strike: float = Autocall.model_fields['call_strike'].default, 
                call_leverage: float = Autocall.model_fields['call_leverage'].default,
                call_cap: float = Autocall.model_fields['call_cap'].default,
                put_strike: float = Autocall.model_fields['put_strike'].default,
                put_barrier: float = Autocall.model_fields['put_barrier'].default,
                put_leverage: float = Autocall.model_fields['put_leverage'].default,
                put_barrier_observ: str = Autocall.model_fields['put_barrier_observ'].default,
                kg: float = Autocall.model_fields['kg'].default):
        
        # Definition of the triggers arrays
        n_obs_recall = DICT_MATCH_FREQ[recall_freq]
        arr_recall_triggers = build_trigger_array(first_trigger, step_down, start_recall, n_obs_recall * maturity)
        arr_coupon_triggers = build_trigger_array(coupon_trigger, 0, start_coupon, n_obs_recall * maturity)
        arr_coupons = np.ones(len(arr_coupon_triggers)) * coupon


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
            start_coupon=start_coupon,
            is_memory=is_memory,
            call_strike=call_strike,
            call_leverage=call_leverage,
            call_cap=call_cap,
            put_strike=put_strike,
            put_barrier=put_barrier,
            put_leverage=put_leverage,
            put_barrier_observ=put_barrier_observ,
            kg=kg,
            arr_recall_trigger=arr_recall_triggers,
            arr_coupon_trigger=arr_coupon_triggers,
            arr_coupons=arr_coupons
        )

    

class Athena(Autocall):

    @classmethod            # Allows to instantiate an object using default values when missing arguments
    def from_params(cls,        
                strike_date: DateModel = Autocall.model_fields['strike_date'].default,
                underlying: Underlying = Autocall.model_fields['underlying'].default,
                maturity: float = Autocall.model_fields['maturity'].default,
                currency: str = Autocall.model_fields['currency'].default,
                start_recall: int = Autocall.model_fields['start_recall'].default,
                recall_freq: str = Autocall.model_fields['recall_freq'].default,
                first_trigger: float = Autocall.model_fields['first_trigger'].default,
                step_down: float = Autocall.model_fields['step_down'].default,
                coupon: float = Autocall.model_fields['coupon'].default,
                start_coupon: int = Autocall.model_fields['start_coupon'].default,
                call_strike: float = Autocall.model_fields['call_strike'].default,
                call_leverage: float = Autocall.model_fields['call_leverage'].default,
                call_cap: float = Autocall.model_fields['call_cap'].default,
                put_strike: float = Autocall.model_fields['put_strike'].default,
                put_barrier: float = Autocall.model_fields['put_barrier'].default,
                put_leverage: float = Autocall.model_fields['put_leverage'].default,
                put_barrier_observ: str = Autocall.model_fields['put_barrier_observ'].default,
                kg: float = Autocall.model_fields['kg'].default):
        
        """
        Default class method to create an instance of an Athena product.
        """

        # In the case of an Athena structure, coupons are paid upon redemption. Therefore coupon and recall triggers are the same
        n_obs_recall = DICT_MATCH_FREQ[recall_freq]
        arr_recall_triggers = build_trigger_array(first_trigger, step_down, start_recall, n_obs_recall * maturity)
        arr_coupons = np.ones(len(arr_recall_triggers)) * coupon


        
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
            coupon_trigger=first_trigger,
            start_coupon=start_coupon, 
            is_memory=True,
            call_strike=call_strike,
            call_leverage=call_leverage,
            call_cap=call_cap,
            put_strike=put_strike,
            put_barrier=put_barrier,
            put_leverage=put_leverage,
            put_barrier_observ=put_barrier_observ,
            kg=kg,
            arr_recall_trigger=arr_recall_triggers,
            arr_coupon_trigger=arr_recall_triggers,
            arr_coupons=arr_coupons
        )