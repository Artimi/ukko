# -*- coding: utf-8 -*-

import numpy as np


class ActivityList(object):

    def __init__(self, num_activities, array=None):
        self.num_activities = num_activities
        if array is None:
            self._array = np.zeros(self.num_activities, dtype=int)
        else:
            self._array = np.array(array, dtype=int)

    def __getitem__(self, item):
        return self._array[item]
