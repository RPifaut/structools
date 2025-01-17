import numpy as np
from structools.tools.date_tools import DateModel
from structools.products.basic_products import Underlying, Basket, Index

"""
File containing default parameters for the tests
"""

START_DATE = DateModel(date="2001-10-22")
END_DATE = DateModel(date="2024-10-22")

L_COMPO = ["AAPL", "MSFT", "^FCHI", "^SPX"]
WEIGHTS = np.array([0.25, 0.25, 0.25, 0.25])
N = 1

BASKET = Basket.from_params(size=1_000_000,
                            name="Custom Basket",
                            worst=False,
                            best=False,
                            N=1,
                            compo=L_COMPO,
                            weights=WEIGHTS)

INDEX = Index.from_params(10000, "Custom Index", "A", L_COMPO, WEIGHTS)


# Autocall Params
UNDL = Underlying()
STRK_DT = START_DATE
MATU = 10
CURRENCY = "EUR"
START_RECALL = 12
RECALL_FREQ = "M"
FIRST_TRIGGER = 1.0
SD = 0.03/12
COUPON = 0.05
COUPON_TRIGG = 0.80
START_COUPON = START_RECALL
MEMO = False
CALL_STRK = 1.0
CALL_LEVERAGE = 1.0
CALL_CAP = 0.3
PUT_STRK = 1.0
PUT_BARR = 0.6
PUT_LEVERAGE = 1.0
PUT_OBS = "EUROPEAN"
KG = 0.0

# Autocall good params
DICT_ATHENA = {
    "strike_date":STRK_DT,
    "underlying":UNDL,
    "maturity":MATU,
    "currency":CURRENCY,
    "start_recall":START_RECALL,
    "recall_freq":RECALL_FREQ,
    "first_trigger":FIRST_TRIGGER,
    "step_down":SD,
    "coupon":COUPON,
    "start_coupon":START_COUPON,
    "call_strike":CALL_STRK,
    "call_leverage":CALL_LEVERAGE,
    "call_cap":CALL_CAP,
    "put_strike":PUT_STRK,
    "put_barrier":PUT_BARR,
    "put_leverage":PUT_LEVERAGE,
    "put_barrier_observ":PUT_OBS,
    "kg":KG
}

DICT_PHOENIX = {
    "strike_date":STRK_DT,
    "underlying":UNDL,
    "maturity":MATU,
    "currency":CURRENCY,
    "start_recall":START_RECALL,
    "recall_freq":RECALL_FREQ,
    "first_trigger":FIRST_TRIGGER,
    "step_down":SD,
    "coupon":COUPON,
    "coupon_trigger":COUPON_TRIGG,
    "is_memory": MEMO,
    "start_coupon":START_COUPON,
    "call_strike":CALL_STRK,
    "call_leverage":CALL_LEVERAGE,
    "call_cap":CALL_CAP,
    "put_strike":PUT_STRK,
    "put_barrier":PUT_BARR,
    "put_leverage":PUT_LEVERAGE,
    "put_barrier_observ":PUT_OBS,
    "kg":KG
}