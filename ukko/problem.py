# -*- coding: utf-8 -*-

import igraph
from utils import memoized


class Problem(object):

    def __init__(self, problem_dict):
        self.problem_dict = problem_dict
        graph_attrs = {'num_resources': self.problem_dict['num_resources'],
                       'res_constraints': self.problem_dict['res_constraints']}
        vertex_attrs = {'duration': self.problem_dict['activities']['duration'],
                        'res_demands': self.problem_dict['activities']['res_demands'].T.tolist()}
        self.graph = igraph.Graph(n=self.problem_dict['num_activities'],
                                  directed=True,
                                  edges=self.problem_dict['edges'],
                                  vertex_attrs=vertex_attrs,
                                  graph_attrs=graph_attrs)

    @memoized
    def predecessors(self, activity):
        return set(self.graph.predecessors(activity))

    @memoized
    def successors(self, activity):
        return set(self.graph.successors(activity))

    def contains_all_predecessors(self, container, activity):
        act_predecessors = self.predecessors(activity)
        return container.intersection(act_predecessors) == act_predecessors

    @property
    def num_activities(self):
        return self.problem_dict['num_activities']

    @property
    def num_resources(self):
        return self.problem_dict['num_resources']

    @property
    def res_constraints(self):
        return self.problem_dict['res_constraints']

    @property
    def activities(self):
        return self.problem_dict['activities']

    def duration(self, activity):
        return self.activities['duration'][activity]

    def demands(self, activity):
        return self.activities['res_demands'][:, activity]
