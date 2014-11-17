# -*- coding: utf-8 -*-
import unittest
import os.path

from ukko import RCPParser, Problem, ActivityList, Schedule, ResourceUtilization, SSGS, RTHypothesis, RTSystem, GARTH
from ukko.utils import PrecedenceException

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '../')
TEST_FILE = PROJECT_ROOT + 'psplib/j30rcp/J301_1.RCP'


class GARTHTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.g = GARTH(self.problem)

    def test_init(self):
        g = GARTH(self.problem)

    def test_step(self):
        self.g.step()
