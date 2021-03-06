# -*- coding: utf-8 -*-

import math
import numpy as np


class ResourceUtilization(object):
    def __init__(self, res_constraints,  num_resources, max_makespan=64):
        self.res_constraints = res_constraints
        self.num_resources = num_resources
        self.max_makespan = max_makespan
        self.utilization = np.zeros([self.num_resources, max_makespan], dtype=np.int)

    def add(self, demands, start_time, finish_time):
        if finish_time > self.max_makespan:
            self.extend_makespan(finish_time)
        self.utilization[:, start_time:finish_time] += demands

    def remove(self, demands, start_time, finish_time):
        self.utilization[:, start_time:finish_time] -= demands

    def extend_makespan(self, minimal_extend_time):
        if minimal_extend_time > self.max_makespan:
            difference = self.max_makespan * math.floor(minimal_extend_time / self.max_makespan)
            extension = np.zeros([self.num_resources, difference], dtype=np.int)
            self.utilization = np.hstack((self.utilization, extension))
            self.max_makespan += difference

    def get(self, resource, time):
        return self.utilization[resource][time]

    def get_capacity(self, resource, time):
        return self.res_constraints[resource] - self.get(resource, time)

    def is_free(self, demands, start_time, finish_time):
        return np.all(self.utilization[:, start_time:finish_time] + demands <= self.res_constraints)