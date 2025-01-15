import pytest
import copy
import numpy as np
from pydantic import ValidationError

from tests.params import *
from src.structools.products.autocalls import Autocall, Athena, Phoenix
from src.structools.products.basic_products import Underlying, Basket

# ------------------------------------------------------------------------------------
# Underlying tests
# ------------------------------------------------------------------------------------

# Testing the correct initialisation of a basket
def test_basket_initialisation():

    # Corretly selected basket
    basket = Basket.from_params(size = 1_000_000, name="Basket Test", worst=True, best=False,
                                    N=1, compo=L_COMPO, weights=WEIGHTS)
    assert isinstance(basket, Underlying)

    with pytest.raises(ValidationError):
        # Wrong not matching number of components and weights
        basket = Basket.from_params(size = 1_000_000, name="Basket Test", worst=True, best=False,
                                        N=4, compo=L_COMPO[:-1], weights=WEIGHTS)
        
        # Wrong weights selection
        basket = Basket.from_params(size = 1_000_000, name="Basket Test", worst=True, best=False,
                                N=4, compo=L_COMPO[:-1], weights=np.arange(len(L_COMPO)))

        # Selecting worst and best of at the same time
        basket = Basket.from_params(size = 1_000_000, name="Basket Test", worst=True, best=True,
                                N=4, compo=L_COMPO[:-1], weights=np.arange(len(L_COMPO)))
        

def test_basket_return_computation():

    basket = Basket.from_params(size = 1_000_000, name="Basket Test", worst=True, best=False,
                                    N=1, compo=L_COMPO, weights=WEIGHTS)
    
    











# ------------------------------------------------------------------------------------
# Autocalls tests
# ------------------------------------------------------------------------------------

# Athena
def test_athena_init():

    # Correct instantiation
    athena = Athena.from_params(**DICT_ATHENA)
    assert isinstance(athena, Autocall)
    assert athena.arr_recall_trigger[10] == 999
    assert athena.arr_recall_trigger[11] == 1.0
    assert athena.arr_recall_trigger[-1] == 0.73

    with pytest.raises(ValidationError):
        # Negative value for the recall trigger
        dict_copy = DICT_ATHENA.copy()
        dict_copy["first_trigger"] = -1.0
        athena = Athena.from_params(**dict_copy)


    with pytest.raises(KeyError):
        # Invalid recall frequency
        dict_copy = DICT_ATHENA.copy()
        dict_copy["recall_freq"] = "P"
        athena = Athena.from_params(**dict_copy)




# Phoenix
def test_phoenix_init():

    # Correct instantiation
    phoenix = Phoenix.from_params(**DICT_PHOENIX)
    assert isinstance(phoenix, Autocall)
    assert phoenix.arr_recall_trigger[10] == 999
    assert phoenix.arr_recall_trigger[11] == 1.0
    assert phoenix.arr_recall_trigger[-1] == 0.73
