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
    g = GARTH(problem)
    g.run()
    print g.best.makespan
    print g.generated_schedules


if __name__ == '__main__':
    main()