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
        self.__dict__.update(problem_dict)

    @memoized
    def predecessors(self, activity):
        return self.graph.predecessors(activity)
