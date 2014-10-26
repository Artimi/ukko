# -*- coding: utf-8 -*-

import numpy as np


class ActivityList(object):

    def __init__(self, problem, array=None):
        self.problem = problem
        if array is None:
            self._array = np.zeros(self.problem.num_activities, dtype=int)
        else:
            self._array = np.array(array, dtype=int)

    def __getitem__(self, item):
        return self._array[item]

    def is_precedence_feasible(self):
        act_previous = set()
        for activity in self:
            if not self.problem.contains_all_predecessors(act_previous, activity):
                return False
            act_previous.add(activity)
        return True
