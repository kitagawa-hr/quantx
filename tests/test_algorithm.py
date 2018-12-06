"""test for quantx.py

[data description]
<class 'pandas.core.panel.Panel'>
Dimensions: 6 (items) x 224 (major_axis) x 3 (minor_axis)
Items axis: open_price to close_price_adj
Major_axis axis: 2018-01-04 to 2018-11-28
Minor_axis axis: jp.stock.3405 to jp.stock.6503
"""

import pickle
import random
import unittest
from logging import Formatter, StreamHandler, getLogger, DEBUG

from tests.utils import generators
from src.algorithm import moving_average
from src.maron import context


class QuantxTests(unittest.TestCase):
    def setUp(self):
        self.logger = getLogger(__name__)
        formatter = Formatter(
            "%(asctime)s - "
            "%(levelname)s - "
            "%(filename)s:%(lineno)d - "
            "%(funcName)s - "
            "%(message)s"
        )
        sh = StreamHandler()
        sh.setFormatter(formatter)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(sh)

        with open("data/data.pickle", "rb") as f:
            data = pickle.load(f)

        self.data = data
        self.date = generators.generate_date
        self.current1 = generators.generate_current(data)
        self.current2 = generators.generate_current(data)
        self.current3 = generators.generate_current(data)
        self.current4 = generators.generate_current(data)
        self.current5 = generators.generate_current(data)
        self.ctx = sample_classes.Context()

    def test_initialize(self):
        algorithm.initialize(self.ctx)
        for name, signal in self.ctx.signals.items():
            self.logger.debug(f"{name} is loaded")
            signal(self.data)

    def test_handle_signals(self):
        currents = filter(
            lambda x: x,
            [self.current1, self.current2, self.current3, self.current4, self.current5],
        )
        for current in currents:
            quantx.handle_signals(self.ctx, self.date, current)
