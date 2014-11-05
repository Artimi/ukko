#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import argparse
from rcpparser import RCPParser
from problem import Problem
from garth import GARTH


def parse_args():
    parser = argparse.ArgumentParser(description='RCPSP Solver')
    parser.add_argument('rcp_file', help='RCP formated file with problem description')
    return parser.parse_args()


def main():
    args = parse_args()
    rcpparser = RCPParser()
    problem_dict = rcpparser(args.rcp_file)
    problem = Problem(problem_dict)
    params = {'popSize': 10,
                   'Rcopy': 0.1,
                   'Rnew': 0.0,
                   'Rmut': 0.2,
                   'Rcross': 0.7,
                   'nSelJobs': 5,
                   'dist': 10000}  # unlimited
    g = GARTH(problem, params)
    g.step()
    print g.best.makespan


if __name__ == '__main__':
    main()