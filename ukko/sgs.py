# -*- coding: utf-8 -*-

import schedule


class SSGS(object):
    def __init__(self, problem):
        self.problem = problem
        self.S = schedule.Schedule(self.problem)

    def get_schedule(self):
        for i in xrange(self.problem.num_activities):
            activity = self._select_activity()
            duration = self.problem.activities['duration'][activity]
            ESj = self._compute_earliest_start(activity)
            Sj = self._compute_real_start(ESj, activity, duration)
            self.S.add(activity, Sj)
        return self.S

    def _select_activity(self):
        return self.S.eligible_activities.pop()

    def _compute_earliest_start(self, activity):
        max_finish_time_predecessors = 0
        for predecessor in self.problem.predecessors(activity):
            if max_finish_time_predecessors < self.S.finish_times_activities[predecessor]:
                max_finish_time_predecessors = self.S.finish_times_activities[predecessor]
        return max_finish_time_predecessors

    def _compute_real_start(self, ESj, activity, duration):
        Sj = 0
        for t in sorted(self.S.finish_times.keys()):
            if ESj <= t and self.S._can_place(activity, t, t + duration):
                Sj = t
                break
        return Sj