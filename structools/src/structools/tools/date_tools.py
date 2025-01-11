import numpy as np
import pandas as pd
from datetime import datetime, date
from pydantic import BaseModel, field_validator
from datetime import date
from dateutil.relativedelta import relativedelta


# ---------------------------------------------------------------------------------------------
# Main variables
# ---------------------------------------------------------------------------------------------


# List with the possible recall frequencies: Weekly, Monthly, Quarterly, Semi-Annually, Annually
L_FREQ = ["W", "M", "Q", "S", "A"]

# Dictionary to match the frequencies (str) with the number of observations per year
DICT_MATCH_FREQ = {
    "W" : 52,
    "M" : 12,
    "Q" : 4,
    "S" : 2, 
    "A" : 1
}


# ---------------------------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------------------------


class DateModel(BaseModel):

    date : np.datetime64

    # Allow Pydantic to recognize the numpy.datetime64 type
    class Config:
        arbitrary_types_allowed = True

    @field_validator("date", mode="before")
    def convert_to_datetime64(cls, value):

        """
        Function that converts different types of dates to np.datetime64 to ensure
        smooth functioning of the package.
        
        Parameters:

            value (any): Date object to be used (can be of any type).

        Returns:

            date (DateModels): DateModel object of type np.datetime64
        """

        if isinstance(value, np.datetime64):
            return np.datetime64(value, "D")
        elif isinstance(value, (datetime, date)):
            return np.datetime64(value, "D")
        elif isinstance(value, str):
            try:
                return np.datetime64(datetime.fromisoformat(value), "D")
            except:
                raise ValueError(f"Invalid date: {value}")
        else:
            raise TypeError(f"Selected type not supported")
        
    
    def to_str(self) -> str:

        """
        Function that returns a string representation of the date it represents.
        """

        return np.datetime_as_string(self.date, 'D')
    



# ---------------------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------------------

    
def find_dates_index(ref_date : np.datetime64, n_obs : int, freq : str, index : np.ndarray):

    """
    Function that returns an array containing the observation dates given a array of dates.

    Parameters:

        - ref_date: Reference date, starting point for the search
        - n_obs: Number of observation from the strike date.
        - freq: Frequency of the observations.    
        - index: Array (pd.Index-like) containing a set of possible observation dates.

    Returns:

        - arr_dates: Array containing the real observation dates.
    """


    # Variables check
    if freq not in L_FREQ:
        raise ValueError(f"Frequency not support. Possible values: {L_FREQ}")
    
    # Convert to datetime for easier use with relativedelta
    ref_date = pd.Timestamp(ref_date).to_pydatetime()
    

    # Find the next theoretical date to find a match in the index
    if freq == "W":
        dates_to_match = [ref_date + relativedelta(weeks = 1 + i) for i in range(n_obs)]
    elif freq == "M":
        dates_to_match = [ref_date + relativedelta(months = 1 + i) for i in range(n_obs)]
    elif freq == "Q":
        dates_to_match = [ref_date + relativedelta(months = 3 * (1 + i)) for i in range(n_obs)]
    elif freq == "S":
        dates_to_match = [ref_date + relativedelta(months = 6 * (1 + i)) for i in range(n_obs)]
    else:
        dates_to_match = [ref_date + relativedelta(years = 1 + i) for i in range(n_obs)]

    # Convert back to np.datetime64
    dates_to_match = list(
        map(
            lambda date: np.datetime64(date.strftime("%Y-%m-%d")),
            dates_to_match
        )
    )

    # Find the index
    matched_indices = np.searchsorted(index, dates_to_match)

    return matched_indices