# -*- coding: utf-8 -*-

import numpy as np
import random
from utils import PrecedenceException


class ActivityList(object):

    def __init__(self, problem, array=None):
        self.problem = problem
        if array is None:
            self._array = np.zeros(self.problem.num_activities, dtype=int)
        else:
            self._array = np.array(array, dtype=int)
            if not self.is_precedence_feasible():
                raise PrecedenceException("Given array is not precedence feasible.")

    def __getitem__(self, item):
        return self._array[item]

    def __iter__(self):
        return self._array.__iter__()

    def is_precedence_feasible(self):
        act_previous = set()
        for activity in self:
            if not self.problem.contains_all_predecessors(act_previous, activity):
                return False
            act_previous.add(activity)
        return True

    def generate_random(self):
        assigned_activities = set()
        maystart = [0]
        for i in xrange(0, self.problem.num_activities):
            activity = random.choice(maystart)
            self._array[i] = activity
            assigned_activities.add(activity)
            maystart.remove(activity)
            for succ in self.problem.successors(activity):
                if self.problem.contains_all_predecessors(assigned_activities, succ):
                    maystart.append(succ)
        return self
