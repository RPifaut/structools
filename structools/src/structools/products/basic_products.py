import numpy as np
from pydantic import BaseModel, Field, validator
from src.structools.tools.date_tools import DateModel

L_OPTIONS = ["CALL", "PUT"]



class Underlying:


    """
    
    General class for the modelling of the underlyings. The types currently available are:
    - Single stock/index
    - N Worst-Of Baskets
    - N Best-Of Baskets
    - Equally Weighted Baskets
    - Custom Weights Baskets

    """

    size : int = 1                      # Number of components in the underlying, default: 1
    N : int = 1                         # Number of the components used for the compute the underlying performance, default: 1
    WORST : bool = False                # True  if the underlying is a Worst-Of
    BEST : bool = False                 # True if the underlying is a Best-Of
    WEIGHTS : np.array = np.array([1])  # Array containing the weights assigned to each underlying in the case of a custom basket, default: np.array([1])


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