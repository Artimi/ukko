# -*- coding: utf-8 -*-

from __future__ import division
import math
from utils import ConstraintException
from activity_list import ActivityList
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Schedule(object):
    RIGHT_SHIFT = 1
    LEFT_SHIFT = -1

    def __init__(self, problem):
        self.problem = problem
        self.start_times = dict()
        self.finish_times = dict()
        self.res_utilization = ResourceUtilization(problem)
        self.scheduled_activities = set()
        self.finish_times_activities = dict()
        self.start_times_activities = dict()

    def _add_to_list(self, activity, l, time):
        try:
            l[time].append(activity)
        except KeyError:
            l[time] = [activity]

    def add(self, activity, start_time):
        finish_time = start_time + self.problem.duration(activity)
        if self.can_place(activity, start_time):
            self._add_to_list(activity, self.start_times, start_time)
            self._add_to_list(activity, self.finish_times, finish_time)
            self.res_utilization.add(self.problem.demands(activity), start_time, finish_time)
            self.scheduled_activities.add(activity)
            self.finish_times_activities[activity] = finish_time
            self.start_times_activities[activity] = start_time
        else:
            raise ConstraintException('Activity {0} cannot be placed at time {1} because of constraints'.format(activity, start_time))

    def remove(self, activity):
        try:
            finish_time = self.finish_times_activities[activity]
        except KeyError:
            raise KeyError("Activity {0} has not been scheduled yet.".format(activity))
        duration = self.problem.duration(activity)
        start_time = finish_time - duration
        self.start_times[start_time].remove(activity)
        self.finish_times[finish_time].remove(activity)
        self.scheduled_activities.remove(activity)
        del self.finish_times_activities[activity]
        del self.start_times_activities[activity]
        self.res_utilization.remove(self.problem.demands(activity), start_time, finish_time)

    def can_place(self, activity, start_time):
        finish_time = start_time + self.problem.duration(activity)
        res_free = self.res_utilization.is_free(self.problem.demands(activity), start_time, finish_time)
        precedence = self.problem.contains_all_predecessors(self._finished_activities(start_time), activity)
        return res_free and precedence

    def earliest_precedence_start(self, activity):
        max_finish_time_predecessors = 0
        for predecessor in self.problem.predecessors(activity):
            try:
                if max_finish_time_predecessors < self.finish_times_activities[predecessor]:
                    max_finish_time_predecessors = self.finish_times_activities[predecessor]
            except KeyError:
                pass
        return max_finish_time_predecessors

    def latest_precedence_start(self, activity):
        duration = self.problem.duration(activity)
        min_finish_time_successors = self.makespan
        for successor in self.problem.successors(activity):
            if min_finish_time_successors > self.start_times_activities[successor]:
                min_finish_time_successors = self.start_times_activities[successor]
        return min_finish_time_successors - duration

    def _finished_activities(self, time):
        result = set()
        for t in xrange(time + 1):
            try:
                result.update(self.finish_times[t])
            except KeyError:
                pass
        return result

    @property
    def eligible_activities(self):
        # improve
        result = set()
        for activity in xrange(self.problem.num_activities):
            if activity not in self.scheduled_activities and self.problem.contains_all_predecessors(self.scheduled_activities, activity):
                result.add(activity)
        return result

    @property
    def makespan(self):
        try:
            makespan = max(self.finish_times.keys())
        except ValueError:
            makespan = 0
        return makespan

    def array_representation(self):
        arrays = []
        activity_corner = []
        for res in xrange(self.problem.num_resources):
            arrays.append(np.zeros((self.problem.res_constraints[res], self.makespan), dtype=int))
            activity_corner.append(dict())
        for time in sorted(self.start_times):
            for activity in self.start_times[time]:
                duration = self.problem.duration(activity)
                res_demands = self.problem.demands(activity)
                for res in xrange(self.problem.num_resources):
                    if res_demands[res] > 0:
                        res_offset = 0
                        while not np.all(arrays[res][res_offset:res_offset+res_demands[res], time:time+duration] == 0):
                            res_offset += 1
                        arrays[res][res_offset:res_offset+res_demands[res], time:time+duration] += activity
                        activity_corner[res][activity] = (time, res_offset)
        return arrays, activity_corner

    def plot(self, figsize=(7,7)):
        arrays, activity_corner = self.array_representation()
        flatui = ["#ffffff", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
        cmap = sns.blend_palette(flatui, as_cmap=True)
        sns.set_style("white")
        plt.figure(figsize=figsize)
        for index, res in enumerate(arrays):
            plt.subplot(self.problem.num_resources, 1, index + 1)
            plt.title('Resource #{0}'.format(index))
            plt.ylim((0, self.problem.res_constraints[index] + 1))
            plt.ylabel('Resource utilization')
            plt.xlabel('Time')
            for activity, coor in activity_corner[index].items():
                plt.annotate(str(activity), coor)
            plt.imshow(res, interpolation='none', cmap=cmap, origin='lower', aspect='auto')
        plt.tight_layout()
        plt.plot()

    def save_plot(self, file_name, figsize=(7,7)):
        self.plot(figsize=figsize)
        plt.savefig(file_name)

    def shift(self, direction=RIGHT_SHIFT):
        if direction == self.RIGHT_SHIFT:
            activity_list = sorted(self.start_times.items(), reverse=True)
        elif direction == self.LEFT_SHIFT:
            activity_list = sorted(self.start_times.items())
        for start_time, activities in activity_list:
            for activity in activities:
                if activity == 0:
                    continue
                self.remove(activity)
                if direction == self.RIGHT_SHIFT:
                    time_list = xrange(self.latest_precedence_start(activity), start_time - 1, -1)
                elif direction == self.LEFT_SHIFT:
                    time_list = xrange(self.earliest_precedence_start(activity), start_time + 1)
                for t in time_list:
                    if self.can_place(activity, t):
                        self.add(activity, t)
                        break

    def double_justification(self):
        makespan = self.makespan
        new_makespan = 0
        while new_makespan < makespan:
            self.shift(self.RIGHT_SHIFT)
            self.shift(self.LEFT_SHIFT)
            new_makespan = self.makespan

    def serialize(self):
        al = ActivityList(self.problem)
        index = 0
        for t, activities in sorted(self.start_times.items()):
            for activity in activities:
                al[index] = activity
                index += 1
        return al


class ResourceUtilization(object):
    def __init__(self, problem, max_makespan=16):
        self.problem = problem
        self.max_makespan = max_makespan
        self.utilization = np.zeros([self.problem.num_resources, max_makespan], dtype=int)

    def add(self, demands, start_time, finish_time):
        if finish_time > self.max_makespan:
            self.extend_makespan(finish_time)
        demands_array = np.expand_dims(demands, 1)
        self.utilization[:, start_time:finish_time] += demands_array

    def remove(self, demands, start_time, finish_time):
        # test if we can subtract?
        demands_array = np.expand_dims(demands, 1)
        result = self.utilization[:, start_time:finish_time] - demands_array
        if not np.all(result >= 0):
            raise KeyError("Cannot remove this demands.")
        else:
            self.utilization[:, start_time:finish_time] = result

    def extend_makespan(self, minimal_extend_time):
        if minimal_extend_time > self.max_makespan:
            difference = self.max_makespan * math.floor(minimal_extend_time / self.max_makespan)
            extension = np.zeros([self.problem.num_resources, difference])
            self.utilization = np.hstack((self.utilization, extension))
            self.max_makespan += difference

    def get(self, resource, time):
        return self.utilization[resource][time]

    def get_capacity(self, resource, time):
        return self.problem.res_constraints[resource] - self.get(resource, time)

    def is_free(self, demands, start_time, finish_time):
        if demands.shape != self.problem.res_constraints.shape:
            demands_array = np.expand_dims(demands, 1)
        else:
            demands_array = demands
        return np.all(self.utilization[:, start_time:finish_time] + demands_array <= self.problem.res_constraints)
