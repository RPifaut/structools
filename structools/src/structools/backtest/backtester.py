import logging
from typing import List, Union
from pydantic import BaseModel, Field
from dateutil.relativedelta import relativedelta

from src.structools.tools.market import Market
from src.structools.tools.date_tools import DateModel
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

        