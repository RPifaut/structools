import numpy as np
import pandas as pd
import plotly.graph_objects as go

import logging
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List
from structools.tools.date_tools import DateModel
from structools.tools.market import Market, L_PRICES

logging.basicConfig(level=logging.INFO)

L_OPTIONS = ["CALL", "PUT"]



class Underlying(BaseModel):

    class Config:

        arbitrary_types_allowed = True
        extra = "forbid"
        frozen = False

    size : float = Field(1,
                         description="Nominal invested on the basket"
    )
    name : str = Field(default="AAPL")            
    N : int = Field(1,
                    description="In the case of Worst-Of/Best/Of. Number of assets to consider"
    )                  
    WORST : bool = Field(False)                
    BEST : bool = Field(False)      
    COMPO : List[str] = Field(
        default=["AAPL"],
        description="List of components in the Underlying.",
        min_items=1
    ) 
    WEIGHTS : np.ndarray = Field(
        default=np.array([1]),
        description="Array of weights for the underlying."
    )
    market : Market = Field(None)


    # Field validators
    @field_validator("WEIGHTS", mode="before")
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
        
        # Check that the weights sum up to 1
        if np.round(sum(arr_weights), 5) != 1:
            raise ValueError(f"The weights of the custom basket must sum up to 1. Here, the sum equals {sum(arr_weights)}.")
        
        logging.info("Weights selection validated.")
        
        return arr_weights
    

    # Model validation
    @model_validator(mode="after")
    def validate_selection(self):

        # Check Worst-Of/Best-Of Compatibility
        if self.WORST and self.BEST:
            raise ValueError("Incompatible selection: the basket cannot be both Worst and Best-Of.")

        # Check the compatilibility of the number of components to be considered for the Worst/best of computation
        if self.N > len(self.COMPO):
            raise ValueError(f"Incompatible selection: cannot have more worst/best of  {self.N} elements than basket underlyings {len(self.COMPO)}.")   
        
        # Check compatibility between weights and number of assets
        if len(self.COMPO) != len(self.WEIGHTS):
            raise ValueError(f"Lengths of weights and composition do not match. Got {len(self.COMPO)} components for {len(self.WEIGHTS)} weights.")

        logging.info("Coherent Selection of the basket components. Basket successfully created!")

        return self

    @classmethod
    def from_params(self, *args, **kwargs):

        pass
    
    def compute_return_compo(self, tickers : List[str], start_date : DateModel, end_date : DateModel, uniform : bool = True, market : Market = None):

        pass

    def build_track(self, start_date : DateModel, end_date : DateModel, df_perf : pd.DataFrame = None):

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
                    N,
                    compo,
                    weights):

        logging.info("Build the basket...")
        
        return cls(size=size,
                   name=name,
                   WORST=worst,
                   BEST=best,
                   N=N,
                   COMPO=compo,
                   WEIGHTS=weights)
    

    def compute_return_compo(self, start_date : DateModel, end_date : DateModel, uniform : bool = True, market : Market = None, price : str = 'Close') -> pd.DataFrame:

        """
        Method to compute the return of a Basket

        Parameters:

            start_date(DateModel): Date from which we start loading the data from
            end_date (DateModel): Date at which we stop loading the data
            uniform (bool): Only keep the values for which quotations for all the composants are available. Default is true
            price (str): Type of price to be used to compute the Basket's Performance
        
        Return:

            df_perf (pd.DataFrame): Pandas DataFrame containing the returns of the basket's components

        """

        # Input validation
        if end_date.date < start_date.date:
            raise ValueError("Start date cannot be before end date.")

        if price not in L_PRICES:
            raise ValueError(f"Type of price not supported. Available price types: {L_PRICES}")
        
        # Load the data
        if not market:
            logging.info("MISSING Market. Retrieving market data...")
            market = Market.create_market(self.COMPO, start_date, end_date, uniform)
            logging.info("Market Data Sucessfullu loaded.")

        # Create a dataframe with the values we are interested in
        df_perf = pd.DataFrame(
            index = market.data[list(market.data.keys())[0]].index,
            columns = self.COMPO
        )

        # Create the output DataFrame
        for ticker in market.data:
            df_perf[ticker]=market.data[ticker][price].pct_change().fillna(0)

        logging.info("Return computation successfully completed.")

        return df_perf
    

    def build_track(self, start_date : DateModel, end_date : DateModel, df_perf : pd.DataFrame = None) -> pd.DataFrame:

        """
        This method build the track of the basket.

        Parameters:

            start_date (DateModel): Start date of the track
            end_date (DateModel): End date of the track
            df_perf (pd.DataFrame): Components performance
        
        Returns:

            df_track (pd.DataFrame): Pandas DataFrame containing the underlying's track

        """

        # Check whether we have the data to compute the performance
        if df_perf is None:
            logging.info("MISSING components return. Loading the missing data.")
            df_perf = self.compute_return_compo(start_date, end_date)  # Only take Close price
        

        # Create output DataFrame
        df_track = pd.DataFrame(
            index=df_perf.index,
            columns=[self.name, "Return"]
        )

        # Default case of weighted basket
        df_track[self.name] = df_perf.to_numpy().dot(self.WEIGHTS)
        df_track[self.name] = (df_track[self.name] + 1).cumprod()

        # Case of N Worst-Of/Best-Of
        df_perf = df_perf + 1
        df_perf = df_perf.cumprod()

        if self.WORST or self.BEST:

            if self.N > len(df_perf.columns):
                raise ValueError(f"Cannot compute {self.N} extreme performer from a basket containing {len(df_perf.columns)} stocks.")
            
            # Sort the rows by ascending order of performance
            sorted_data = df_perf.to_numpy()
            arr_weights = np.ones(self.N) * 1/self.N
            sorted_data = np.sort(sorted_data)

            sorted_data = sorted_data[:, :self.N].dot(arr_weights) if self.WORST else sorted_data[:, -self.N:].dot(arr_weights)

            df_track[self.name] = sorted_data
            df_track.fillna(1, inplace=True)
        
        df_track["Return"] = df_track[self.name].pct_change()

        logging.info(f"Track successfully built for {self.name}.")

        return df_track
    

    def plot_track(self, start_date : DateModel, end_date : DateModel, df_perf : pd.DataFrame = None, 
                   df_track : pd.DataFrame = None, with_compo : bool = True):

        """
        Method that plots the baskets track for a given date.

        Parameters

            - start_date (DateModel): Start date of the track
            - end_date (DateModel): End date of the track
            - df_perf (pd.DataFrame): DataFrame containing the returns of the basket's components
            - df_track (pd.DataFrame) : DataFrame containing the returns of the basket itself
            - with_compo (pd.DataFrame) : Boolean to decide whether to plot the components alongside the index

        Returns:

            - fig (px.Figure): Plotly Figure object 

        """

        # Check whether all the necessary data has been provided
        if df_track is None:
            logging.info("MISSING Track record. Loading the data and building the track record.")
            df_track = self.build_track(start_date, end_date, df_perf)
        if df_perf is None and with_compo:
            logging.info("MISSING components returns. Loading the data.")
            df_perf = self.compute_return_compo(start_date, end_date)

        # Create the figure
        fig = go.Figure()

        # Plot the components if required
        if with_compo:
            df_perf = (df_perf + 1).cumprod()
            for elem in df_perf.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df_perf.index, 
                        y=df_perf.loc[:, elem],
                        mode='lines',
                        name=elem
                    )
                )

        # Plotting the track of the basket
        fig.add_trace(
            go.Scatter(
                x=df_track.index, 
                y=df_track[self.name],
                mode='lines',
                name=self.name,
                line=dict(width=2, color='black')
            )
        )

        return fig



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

    @field_validator("option_type", mode="before")
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
