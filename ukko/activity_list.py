# -*- coding: utf-8 -*-

import numpy as np
import random
from utils import PrecedenceException


class ActivityList(object):
    RIGHT_SHIFT = 1
    LEFT_SHIFT = -1

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

    def __setitem__(self, key, value):
        self._array[key] = value

    def __iter__(self):
        return self._array.__iter__()

    def __str__(self):
        return str(self._array)

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

    def shift(self, activity, direction, steps):
        index = np.where(self._array == activity)[0][0]
        i = 0
        for i in xrange(steps):
            current_index = index + i * direction
            next_index = current_index + direction
            try:
                if next_index < self.problem.num_activities:
                    self._swap(current_index, current_index + direction)
                else:
                    break
            except PrecedenceException:
                break
        else:
            return i + 1
        return i

    def _swap(self, index1, index2):
        lower_index = index1 if index1 < index2 else index2
        higher_index = index1 if index1 > index2 else index2
        if self._array[lower_index] not in self.problem.predecessors_all(self._array[higher_index]):
            self._array[index1], self._array[index2] = self._array[index2], self._array[index1]
        else:
            raise PrecedenceException("Swap of {0} and {1} would break precedence condition.".format(self._array[lower_index], self._array[higher_index]))

    def crossover(self, other, c1, c2):
        child = ActivityList(self.problem)
        child[:c1] = self[:c1]
        index = c1
        for act in other:
            if act not in child[:c1]:
                child[index] = act
                index += 1
        index = c2
        for act in self[c1:]:
            if act not in child[:c2]:
                child[index] = act
                index += 1
        return child
