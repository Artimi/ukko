# -*- coding: utf-8 -*-

import numpy as np
from itertools import combinations, product


class RTHypothesis(object):
    PSE = 0
    FLE = 1
    SLT = 2

    INFINITY = np.iinfo(int).max

    def __init__(self, problem, characteristic):
        self.problem = problem
        self.characteristic = characteristic
        self._array = np.empty((self.problem.num_activities, self.problem.num_activities), dtype=int)
        self._array[:, :] = self.INFINITY

    def __getitem__(self, item):
        return self._array[item]

    def update(self, schedule):
        if self.characteristic == self.PSE:
            self._update_PSE(schedule)
        elif self.characteristic == self.FLE:
            self._update_FLE(schedule)
        elif self.characteristic == self.SLT:
            self._update_SLT(schedule)

    def get_excluding(self):
        result = []
        max_time = self._array[self._array < self.INFINITY].max()
        activities = np.argwhere(self._array == max_time)
        for couple in activities:
            result.append(tuple(couple))
        return result

    def _update_PSE(self, schedule):
        makespan = schedule.makespan
        for activities in schedule.start_times.values():
            for couple in combinations(activities, 2):
                if self._array[couple] > makespan:
                    self._array[couple] = makespan

    def _update_FLE(self, schedule):
        makespan = schedule.makespan
        previous_activities = set()
        for activities in schedule.finish_times.values():
            previous_activities.update(activities)
            for couple in product(previous_activities, activities):
                if self._array[couple] > makespan:
                    self._array[couple] = makespan

    def _update_SLT(self, schedule):
        makespan = schedule.makespan
        previous_activities = set()
        for activities in schedule.start_times.values():
            for couple in product(previous_activities, activities):
                if self._array[couple] > makespan:
                    self._array[couple] = makespan
            previous_activities.update(activities)
