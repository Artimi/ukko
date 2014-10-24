# -*- coding: utf-8 -*-


class RCPParser(object):

    def __call__(self, file_path):
        result = {}
        lines = self._read_lines(file_path)
        result['num_activities'],result['num_resources'] = lines[0]
        result['res_constraints'] = lines[1]
        result['activities'] = self._parse_activites(lines[2:], result['num_resources'])
        return result

    @staticmethod
    def _read_lines(file_path):
        with open(file_path) as f:
            lines = f.readlines()
        return [map(int, line) for line in [line.split() for line in lines]]

    @staticmethod
    def _parse_activites(lines, num_resources):
        result = {}
        for index, line in enumerate(lines):
            result[index] = {}
            result[index]['duration'] = line[0]
            index_num_successors = num_resources + 1
            result[index]['res_demands'] = line[1:index_num_successors]
            result[index]['num_successors'] = line[index_num_successors]
            result[index]['successors'] = line[index_num_successors+1:]
        return result


