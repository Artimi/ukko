# -*- coding: utf-8 -*-
import argparse
from rcpparser import RCPParser


def parse_args():
    parser = argparse.ArgumentParser(description='RCPSP Solver')
    parser.add_argument('rcp_file', help='RCP formated file with problem description')
    return parser.parse_args()


def main():
    args = parse_args()
    rcpparser = RCPParser()
    problem_dict = rcpparser(args.rcp_file)
    print problem_dict


if __name__ == '__main__':
    main()