import numpy as np
from pydantic import BaseModel, Field, validator
from typing import List
from src.structools.tools.date_tools import DateModel

L_OPTIONS = ["CALL", "PUT"]



class Underlying(BaseModel):

    class Config:

        arbitrary_types_allowed=True


    size : int = Field(1)
    name : str                      
    N : int = Field(1)                  
    WORST : bool = False                
    BEST : bool = False      
    COMPO : List[str] = Field(
        default_factory=list,
        description="List of components in the Underlying.",
        min_items=1
    ) 
    WEIGHTS : np.ndarray = Field(
        default_factory=lambda: np.array([]),
        description="Array of weights for the underlying."
    )

    @validator("WEIGHTS", pre=True)
    def validate_weights(cls, arr_weights):

        # Check whether the list is empty of not
        if isinstance(arr_weights, np.ndarray):
            if len(list(arr_weights)) == 0:
                raise ValueError(f"Weights list cannot be empty.")
        
        # Check the validity of the input
        if not np.issubdtype(arr_weights.dtype, np.number):
            raise TypeError(f"Array can only contain integers or floats. Got {arr_weights.dtype}.")
        
        return arr_weights


class OptionBaseModel(BaseModel):

    option_type : str
    strike_date : DateModel
    spot : float = Field(100.0, ge=0)
    strike_price : float = Field(100.0, ge=0)
    rate : float = Field(0.01, ge=0)
    div_yield : float = Field(0.01, ge=0)
    vol : float = Field(0.15, ge=0)
    time_to_maturity : float = Field(0.25, ge=0)

    class Config:

        arbitrary_types_allowed = True


    @validator("option_type", pre=True)
    def verify_type(cls, value):

        if value.upper() in L_OPTIONS:
            return value
        else:
            raise ValueError(f"Option type not supported. Admissible types are: {L_OPTIONS}.")


class Option(OptionBaseModel):


    @classmethod
    def from_params(cls,
        option_type,
        strike_date,
        spot,
        strike_price,
        rate,
        div_yield,
        vol,
        time_to_maturity
    ):
        
        return cls(
            option_type=option_type,
            strike_date=strike_date,
            spot=spot,
            strike_price=strike_price,
            rate=rate,
            div_yield=div_yield, 
            vol=vol,
            time_to_maturity=time_to_maturity
        )