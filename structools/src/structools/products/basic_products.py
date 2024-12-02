import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator
from typing import List
from src.structools.tools.date_tools import DateModel
from src.structools.tools.market import Market, L_PRICES

L_OPTIONS = ["CALL", "PUT"]



class Underlying(BaseModel):

    class Config:

        arbitrary_types_allowed = True
        extra = "forbid"
        frozen = False


    size : float = Field(1)
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
    market : Market = None

    @validator("WEIGHTS", pre=True)
    def validate_weights(cls, arr_weights):

        # Check whether the list is empty of not
        if not isinstance(arr_weights, np.ndarray):
            raise TypeError(f"Expected type np.ndarray. Got {type(arr_weights).__name__}.")
        
        if isinstance(arr_weights, np.ndarray):
            if len(list(arr_weights)) == 0:
                raise ValueError(f"Weights list cannot be empty.")
        
        # Check the validity of the input
        if not np.issubdtype(arr_weights.dtype, np.number):
            raise TypeError(f"Array can only contain integers or floats. Got {arr_weights.dtype}.")
        
        return arr_weights
    
    def compute_performance(self, tickers : List[str], start_date : DateModel, end_date : DateModel, uniform : bool = True):

        pass
    

    # --------------------------------------------------------------------
    # Common Methods to all Underlyings
    # --------------------------------------------------------------------

    def set_parameter(self, attribute_name : str, value):

        if attribute_name not in self.__fields__:
            raise AttributeError(f"Impossible to create or change the value of attribute {attribute_name}.")
        
        if not isinstance(value, type(getattr(self, attribute_name))):
            raise TypeError(f"Expected {type(getattr(self, attribute_name)).__name__}. Got {type(value).__name__}")
        
        setattr(self, attribute_name, value)


class Basket(Underlying):

    """
    Class for the representation of a basket of stocks.
    """

    @classmethod
    def from_params(cls, 
                    size,
                    name,
                    worst, 
                    best,
                    compo,
                    weights):
        
        return cls(size=size,
                   name=name,
                   WORST=worst,
                   BEST=best,
                   COMPO=compo,
                   WEIGHTS=weights)
    

    def compute_performance(self, start_date : DateModel, end_date : DateModel, uniform : bool = True, price : str = 'Close'):

        """
        Method to compute the performance of a Basket taking into consideration the weighting scheme, worst-of/best-of.

        Parameters:

            start_date(DateModel): Date from which we start loading the data from
            end_date (DateModel): Date at which we stop loading the data
            uniform (bool): Only keep the values for which quotations for all the composants are available. Default is true
            price (str): Type of price to be used to compute the Basket's Performance

        """

        # Input validation
        if end_date.date < start_date.date:
            raise ValueError("Start date cannot be before end date.")

        if price not in L_PRICES:
            raise ValueError(f"Type of price not supported. Available price types: {L_PRICES}")
        
        # Load the data
        market = Market.create_market(self.COMPO, start_date, end_date, uniform)

        # Create a dataframe with the values we are interested in
        df_track = pd.DataFrame(
            index = market.data[list(market.data.keys())[0]].index,
            columns = self.COMPO
        )

        # Fill in the dataframe
        for ticker in self.COMPO:
            df_track[ticker] = market.data[ticker][price]

        # Create a DataFrame for the performance
        df_perf = df_track.pct_change()
        df_perf["Weighted"] = df_perf.to_numpy().dot(self.WEIGHTS)

        return df_perf
        



class OptionBaseModel(BaseModel):

    class Config:

        arbitrary_types_allowed = True
        extra = "forbid"

    option_type : str
    strike_date : DateModel
    spot : float = Field(100.0, ge=0)
    strike_price : float = Field(100.0, ge=0)
    rate : float = Field(0.01, ge=0)
    div_yield : float = Field(0.01, ge=0)
    vol : float = Field(0.15, ge=0)
    time_to_maturity : float = Field(0.25, ge=0)


    # --------------------------------------------------------------------
    # Common Methods to all Options
    # --------------------------------------------------------------------

    @validator("option_type", pre=True)
    def verify_type(cls, value):

        if value.upper() in L_OPTIONS:
            return value
        else:
            raise ValueError(f"Option type not supported. Admissible types are: {L_OPTIONS}.")


    
    # --------------------------------------------------------------------
    # Common Methods to all Options
    # --------------------------------------------------------------------

    def set_parameter(self, attribute_name : str, value):

        if attribute_name not in self.__fields__:
            raise AttributeError(f"Impossible to create or change the value of attribute {attribute_name}.")
        
        if not isinstance(value, type(getattr(self, attribute_name))):
            raise TypeError(f"Expected {type(getattr(self, attribute_name)).__name__}. Got {type(value).__name__}")
        
        setattr(self, attribute_name, value)


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