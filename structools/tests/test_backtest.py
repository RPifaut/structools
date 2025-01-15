import pytest
import copy
import numpy as np
from pydantic import ValidationError
import plotly.graph_objects as go

from tests.params import *
from src.structools.tools.market import Market
from src.structools.products.autocalls import Autocall, Athena, Phoenix
from src.structools.products.basic_products import Underlying, Basket
from src.structools.backtest.backtester import Backtester