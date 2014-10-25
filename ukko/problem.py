# -*- coding: utf-8 -*-

import igraph


class Problem(object):

    def __init__(self, problem_dict):
        self.problem_dict = problem_dict
        graph_attrs = {'num_resources': self.problem_dict['num_resources'],
                       'res_constraints': self.problem_dict['res_constraints']}
        self.graph = igraph.Graph(n=self.problem_dict['num_activities'],
                                  directed=True,
                                  edges=self.problem_dict['edges'],
                                  vertex_attrs=self.problem_dict['activities'],
                                  graph_attrs=graph_attrs)
        self.__dict__.update(problem_dict)


