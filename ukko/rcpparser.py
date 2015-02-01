# -*- coding: utf-8 -*-

import numpy as np


class RCPParser(object):

    def __call__(self, file_path):
        result = {}
        lines = self._read_lines(file_path)
        result['num_activities'], result['num_resources'] = lines[0]
        result['res_constraints'] = np.array(lines[1], dtype=np.int, ndmin=2).T
        result['activities'], result['edges'] = self._parse_activites(lines[2:],
                                                                      result['num_resources'],
                                                                      result['num_activities'])
        return result

    @staticmethod
    def _read_lines(file_path):
        with open(file_path) as f:
            lines = f.readlines()
        return [map(int, line) for line in [line.split() for line in lines]]

    @staticmethod
    def _parse_activites(lines, num_resources, num_activities):
        result = {'duration': np.zeros(num_activities, dtype=np.int),
                  'res_demands': np.zeros((num_resources, num_activities), dtype=np.int)}
        edges = list()
        for activity, line in enumerate(lines):
            result['duration'][activity] = line[0]
            index_num_successors = num_resources + 1
            result['res_demands'][:, activity] = line[1:index_num_successors]
            successors = [suc - 1 for suc in line[index_num_successors+1:]]
            edges.extend([(activity, suc) for suc in successors])
        return result, edges


