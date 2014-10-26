import unittest
import nose

import numpy as np
from ukko import RCPParser, Problem,  ActivityList, Schedule, ResourceUtilization

TEST_FILE = '../../psplib/j30rcp/J301_1.RCP'


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = RCPParser()
        self.result = self.parser(TEST_FILE)

    def test_basic_info(self):
        self.assertEqual(self.result['num_activities'], 32)
        self.assertEqual(self.result['num_resources'], 4)
        np.testing.assert_array_equal(self.result['res_constraints'], np.array([12, 13, 4, 12], ndmin=2).T)

    def test_activities(self):
        activity = self.result['activities']
        self.assertEqual(activity['duration'][1], 8)
        np.testing.assert_array_equal(activity['res_demands'][:, 1], np.array([4, 0, 0, 0]))


class ProblemTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)

    def test_graph(self):
        self.assertEqual(len(self.problem.graph.vs), self.problem_dict['num_activities'])
        self.assertEqual(self.problem.graph.vs[1]['duration'], 8)
        self.assertListEqual(self.problem.graph.vs[1]['res_demands'], [4, 0, 0, 0])

    def test_dict_class(self):
        self.assertEqual(self.problem.num_activities, self.problem_dict['num_activities'])

    def test_predecessors(self):
        self.assertTrue(self.problem.is_predecessor_of(0, 1))
        self.assertFalse(self.problem.is_predecessor_of(1, 0))
        self.assertTrue(self.problem.is_predecessor_of_list(0, [1, 2, 3]))


class ActivityListTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                      17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)

    def test_get_item(self):
        self.assertEqual(self.al[4], 5)

    def test_iterator(self):
        activities_order_real = [i for i in self.al]
        self.assertListEqual(activities_order_real, self.activities_order)

    def test_precedence_feasibility(self):
        self.assertTrue(self.al.is_precedence_feasible())
        wrong_order = self.activities_order
        wrong_order[0], wrong_order[1] = wrong_order[1], wrong_order[0]
        al_wrong = ActivityList(self.problem, wrong_order)
        self.assertFalse(al_wrong.is_precedence_feasible())


class ScheduleTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                                 17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)
        self.schedule = Schedule(self.problem)

    def test_add(self):
        self.schedule.add(0, 0)
        self.assertIn(0, self.schedule.start_times[0])
        self.assertIn(0, self.schedule.finish_times[0])
        self.schedule.add(1, 0)
        self.assertIn(1, self.schedule.start_times[0])
        self.assertIn(1, self.schedule.finish_times[self.problem_dict['activities']['duration'][1]])

    def test_can_place(self):
        self.assertFalse(self.schedule._can_place(1, 0, 8))  # violated precedence 0->1
        self.schedule.add(0, 0)
        self.assertTrue(self.schedule._can_place(1, 0, 8))
        self.schedule.add(1, 0)
        self.assertFalse(self.schedule._can_place(2, 0, 4))  # violated resource constraints


class ResourceUtilizationTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.ru = ResourceUtilization(self.problem, max_makespan=16)

    def test_add(self):
        self.ru.add([4, 0, 0, 0], 0, 8)
        self.assertTrue(self.ru.get(0, 0), 4)

    def test_extend(self):
        self.ru.add([4, 0, 0, 0], 16, 18)
        self.assertGreaterEqual(self.ru.max_makespan, 18)

    def test_free(self):
        res_constraints = np.array([12, 13, 4, 12], dtype=int)
        self.assertTrue(self.ru.is_free(res_constraints, 0, 5))
        self.ru.add(res_constraints, 0, 5)
        self.assertFalse(self.ru.is_free(np.array([1, 1, 1, 1], ndmin=2).T, 4, 6))

