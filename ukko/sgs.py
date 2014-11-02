# -*- coding: utf-8 -*-

from .schedule import Schedule


class SSGS(object):
    def __init__(self, problem):
        self.problem = problem
        self.S = Schedule(self.problem)

    def get_schedule(self):
        for i in xrange(self.problem.num_activities):
            activity = self._select_activity()
            precedence_feasible_start = self.S.earliest_precedence_start(activity)
            real_start = self._compute_real_start(activity, precedence_feasible_start)
            self.S.add(activity, real_start)
        return self.S

    def _select_activity(self):
        return self.S.eligible_activities.pop()

    def _compute_real_start(self, activity, precedence_feasible_start):
        real_start = 0
        for t in sorted(self.S.finish_times.keys()):
            if precedence_feasible_start <= t and self.S.can_place(activity, t):
                real_start = t
                break
        return real_start


class SSGS_AL(SSGS):
    def __init__(self, problem, activity_list):
        self.activity_list = activity_list
        self.al_iter = self.activity_list.__iter__()
        super(SSGS_AL, self).__init__(problem)

    def _select_activity(self):
        return next(self.al_iter)
