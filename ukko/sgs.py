# -*- coding: utf-8 -*-

from schedule import Schedule


class SSGS(object):
    def __init__(self, problem):
        self.problem = problem

    def get_schedule(self, activity_list):
        S = Schedule(self.problem)
        self.al_iter = activity_list.__iter__()
        for i in xrange(self.problem.num_activities):
            activity = self._select_activity()
            precedence_feasible_start = S.earliest_precedence_start(activity)
            real_start = self._compute_real_start(S, activity, precedence_feasible_start)
            S.add(activity, real_start, force=True)
        return S

    def _select_activity(self):
        return next(self.al_iter)

    def _compute_real_start(self, schedule, activity, precedence_feasible_start):
        real_start = 0
        for t in sorted(schedule.finish_times.keys()):
            if precedence_feasible_start <= t and schedule.can_place(activity, t):
                real_start = t
                break
        return real_start
