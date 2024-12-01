import numpy as np
from datetime import datetime, date
from pydantic import BaseModel, validator
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
# Functions
# ---------------------------------------------------------------------------------------------


class DateModel(BaseModel):

    date : np.datetime64

    # Allow Pydantic to recognize the numpy.datetime64 type
    class Config:
        arbitrary_types_allowed = True

    @validator("date", pre=True)
    def convert_to_datetime64(cls, value):

        """
        Function that converts different types of dates to np.datetime64 to ensure
        smooth functioning of the package.
        
        Parameters:

            value (any): Date object to be used (can be of any type).

        Returns:

            date(DateModels): DateModel object of type np.datetime64
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



def find_dates_index(ref_date : np.datetime64, n_obs : int, freq : str, index : np.ndarray):

    """
    Function that returns an array containing the observation dates given a array of dates.

    Parameters:
        ref_date: Reference date, starting point for the search
        n_obs: Number of observation from the strike date.
        freq: Frequency of the observations.
        index: Array (pd.Index-like) containing a set of possible observation dates.

    Returns:
        arr_dates: Array containing the real observation dates.
    """


    # Variables check
    if freq not in L_FREQ:
        raise ValueError(f"Frequency not support. Possible values: {L_FREQ}")
    

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

    # Find the index
    matched_indices = np.searchsorted(index, dates_to_match)

    return index[matched_indices]


if __name__ == '__main__':

    input_data = [
    {"date": "2023-11-27"},
    {"date": datetime(2023, 11, 27)},
    {"date": date(2023, 11, 27)},
    {"date": np.datetime64("2023-11-27")},
    ]

    for data in input_data:
        validated = DateModel(**data)
        print(validated.date, type(validated.date), type(validated))