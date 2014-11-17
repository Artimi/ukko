import unittest
import nose
import os.path

import numpy as np
from ukko import RCPParser, Problem,  ActivityList, Schedule, ResourceUtilization, SSGS, RTHypothesis, RTSystem, GARTH
from ukko.utils import PrecedenceException

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '../')
TEST_FILE = PROJECT_ROOT + 'psplib/j30rcp/J301_1.RCP'


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

    def test_predecessor_all(self):
        self.assertSetEqual({0}, self.problem.predecessors_all(1))
        self.assertSetEqual({0, 3}, self.problem.predecessors_all(8))
        self.assertSetEqual(set(range(31)), self.problem.predecessors_all(31))
        self.assertSetEqual({0, 2, 3, 7, 8, 11}, self.problem.predecessors_all(13))


class ActivityListTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                                 17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)
        self.activities_order_better = [0,  2,  3, 12,  7,  6,  9,  1,  4, 17,  8, 15, 11, 18, 26, 10, 28,
                                        14,  5, 13, 25, 19, 16, 21, 20, 27, 22, 24, 23, 30, 29, 31]
        self.al_better = ActivityList(self.problem, self.activities_order_better)

    def test_get_item(self):
        self.assertEqual(self.al[4], 5)

    def test_iterator(self):
        activities_order_real = [i for i in self.al]
        self.assertListEqual(activities_order_real, self.activities_order)

    def test_precedence_feasibility(self):
        self.assertTrue(self.al.is_precedence_feasible())
        wrong_order = self.activities_order
        wrong_order[0], wrong_order[1] = wrong_order[1], wrong_order[0]
        self.assertRaises(PrecedenceException, ActivityList, self.problem, wrong_order)

    def test_generate_random(self):
        al = ActivityList(self.problem).generate_random()
        self.assertEqual(type(al), ActivityList)
        al2 = ActivityList(self.problem).generate_random()
        # this will probably hold False for most cases, probably
        self.assertFalse(np.all(al._array == al2._array))
        self.assertTrue(al.is_precedence_feasible())

    def test_shift(self):
        self.assertEqual(0, self.al.shift(0, ActivityList.RIGHT_SHIFT, 1))
        self.assertEqual(2, self.al.shift(1, ActivityList.RIGHT_SHIFT, 2))  # normal swap
        self.assertEqual(0, self.al.shift(1, ActivityList.RIGHT_SHIFT, 1))  # precedence
        self.assertEqual(5, self.al.shift(2, ActivityList.RIGHT_SHIFT, 8))
        self.assertEqual(5, self.al.shift(2, ActivityList.LEFT_SHIFT, 5))
        self.assertEqual(0, self.al.shift(31, ActivityList.LEFT_SHIFT, 31))

    def test_crossover(self):
        child = self.al.crossover(self.al_better, 10, 20)
        self.assertTrue(child.is_precedence_feasible())


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

    def test_remove(self):
        self.assertRaises(KeyError, self.schedule.remove, 0)
        self.schedule.add(0, 0)
        self.schedule.remove(0)
        self.assertNotIn(0, self.schedule.start_times[0])
        self.assertNotIn(0, self.schedule.finish_times[0])
        self.schedule.add(0, 0)
        self.schedule.add(1, 0)
        self.schedule.remove(1)
        self.assertNotIn(1, self.schedule.start_times[0])
        self.assertNotIn(1, self.schedule.finish_times[self.problem_dict['activities']['duration'][1]])

    def test_can_place(self):
        self.assertFalse(self.schedule.can_place(1, 0))  # violated precedence 0->1
        self.schedule.add(0, 0)
        self.assertTrue(self.schedule.can_place(1, 0))
        self.schedule.add(1, 0)
        self.assertFalse(self.schedule.can_place(2, 0))  # violated resource constraints

    def test_makespan(self):
        self.assertEqual(self.schedule.makespan, 0)
        self.schedule.add(0, 0)
        self.assertEqual(self.schedule.makespan, 0)
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.makespan, 8)

    def test_eligible_activities(self):
        self.assertEqual(self.schedule.eligible_activities, {0})
        self.schedule.add(0, 0)
        self.assertEqual(self.schedule.eligible_activities, {1, 2, 3})
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.eligible_activities, {2, 3, 5, 10, 14})

    def test_earliest_start(self):
        self.schedule.add(0, 0)
        self.schedule.add(1, 0)
        self.assertEqual(self.schedule.earliest_precedence_start(5), 8)

    def test_shift(self):
        ssgs = SSGS(self.problem)
        self.schedule = ssgs.get_schedule(self.al)
        initial_makespan = self.schedule.makespan
        self.schedule.shift(Schedule.RIGHT_SHIFT)
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.schedule.shift(Schedule.RIGHT_SHIFT)  # nothing should change
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.schedule.shift(Schedule.LEFT_SHIFT)
        self.assertEqual(len(self.schedule.scheduled_activities), self.problem.num_activities)
        self.assertGreaterEqual(initial_makespan, self.schedule.makespan)  # makespan should be same or better

    def test_serialize(self):
        ssgs = SSGS(self.problem)
        self.schedule = ssgs.get_schedule(self.al)
        al = self.schedule.serialize()
        act1 = 0
        for act2 in al[1:]:
            self.assertLessEqual(self.schedule.start_times_activities[act1],
                                 self.schedule.start_times_activities[act2])
        self.assertTrue(al.is_precedence_feasible())
        self.schedule.shift(Schedule.RIGHT_SHIFT)
        al_shifted = self.schedule.serialize()
        self.assertTrue(al_shifted.is_precedence_feasible())
        self.schedule.shift(Schedule.LEFT_SHIFT)
        al_shifted = self.schedule.serialize()
        self.assertTrue(al_shifted.is_precedence_feasible())


class ResourceUtilizationTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.ru = ResourceUtilization(self.problem, max_makespan=16)

    def test_add(self):
        self.ru.add([4, 0, 0, 0], 0, 8)
        self.assertEqual(self.ru.get(0, 0), 4)
        self.assertEqual(self.ru.get(0, 7), 4)
        self.assertEqual(self.ru.get(0, 8), 0)
        self.assertEqual(self.ru.get(0, 9), 0)

    def test_remove(self):
        self.assertRaises(KeyError, self.ru.remove, [1, 1, 1, 1], 0, 8)
        self.ru.add([4, 0, 0, 0], 0, 8)
        self.ru.remove([4, 0, 0, 0], 0, 8)
        self.assertEqual(self.ru.get(0, 0), 0)
        self.assertEqual(self.ru.get(0, 8), 0)

    def test_extend(self):
        self.ru.add([4, 0, 0, 0], 16, 18)
        self.assertGreaterEqual(self.ru.max_makespan, 18)

    def test_free(self):
        res_constraints = np.array([12, 13, 4, 12], dtype=int)
        self.assertTrue(self.ru.is_free(res_constraints, 0, 5))
        self.ru.add(res_constraints, 0, 5)
        self.assertFalse(self.ru.is_free(np.array([1, 1, 1, 1], ndmin=2).T, 4, 6))


class SSGSTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)

    def test_al(self):
        activities_order = [0, 2, 1, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                            17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        al = ActivityList(self.problem, activities_order)
        ssgs = SSGS(self.problem)
        schedule = ssgs.get_schedule(al)
        self.assertEqual(len(schedule.scheduled_activities), self.problem.num_activities)


class RTHypothesisTestCase(unittest.TestCase):
    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                                 17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)
        ssgs = SSGS(self.problem)
        self.schedule = ssgs.get_schedule(self.al)
        self.activities_order_better = [0,  2,  3, 12,  7,  6,  9,  1,  4, 17,  8, 15, 11, 18, 26, 10, 28,
                                        14,  5, 13, 25, 19, 16, 21, 20, 27, 22, 24, 23, 30, 29, 31]
        self.al_better = ActivityList(self.problem, self.activities_order_better)
        self.schedule_better = ssgs.get_schedule(self.al_better)

    def test_PSE(self):
        rt = RTHypothesis(self.problem, RTHypothesis.PSE)
        rt.update(self.schedule)
        self.assertEqual(rt[0, 3], self.schedule.makespan)
        self.assertEqual(rt[0, 1], self.schedule.makespan)
        rt.update(self.schedule_better)
        self.assertLess(self.schedule_better.makespan, self.schedule.makespan)
        self.assertEqual(rt[0, 3], self.schedule_better.makespan)
        self.assertEqual(rt[0, 1], self.schedule.makespan)

    def test_FLE(self):
        rt = RTHypothesis(self.problem, RTHypothesis.FLE)
        rt.update(self.schedule)
        self.assertEqual(rt[1, 8], self.schedule.makespan)
        self.assertEqual(rt[8, 1], self.schedule.makespan)
        self.assertEqual(rt[8, 8], self.schedule.makespan)
        rt.update(self.schedule_better)
        self.assertLess(self.schedule_better.makespan, self.schedule.makespan)
        self.assertEqual(rt[1, 8], self.schedule_better.makespan)
        self.assertEqual(rt[8, 1], self.schedule.makespan)
        self.assertEqual(rt[8, 8], self.schedule_better.makespan)

    def test_SLT(self):
        rt = RTHypothesis(self.problem, RTHypothesis.SLT)
        rt.update(self.schedule)
        self.assertEqual(rt[1, 8], self.schedule.makespan)
        self.assertEqual(rt[8, 1], RTHypothesis.INFINITY)
        rt.update(self.schedule_better)
        self.assertLess(self.schedule_better.makespan, self.schedule.makespan)
        self.assertEqual(rt[1, 8], self.schedule_better.makespan)

    def test_excluding(self):
        rt = RTHypothesis(self.problem, RTHypothesis.PSE)
        rt.update(self.schedule)
        rt.update(self.schedule_better)
        self.assertIn((0, 1), rt.get_excluding())


class RTSystemTestCase(unittest.TestCase):

    def setUp(self):
        parser = RCPParser()
        self.problem_dict = parser(TEST_FILE)
        self.problem = Problem(self.problem_dict)
        self.activities_order = [0, 1, 2, 3, 5, 10, 14, 6, 7, 12, 4, 8, 9, 25, 11, 18, 26,
                                 17, 15, 13, 28, 19, 20, 16, 24, 27, 21, 30, 22, 23, 29, 31]
        self.al = ActivityList(self.problem, self.activities_order)
        ssgs = SSGS(self.problem)
        self.schedule = ssgs.get_schedule(self.al)
        self.activities_order_better = [0,  2,  3, 12,  7,  6,  9,  1,  4, 17,  8, 15, 11, 18, 26, 10, 28,
                                        14,  5, 13, 25, 19, 16, 21, 20, 27, 22, 24, 23, 30, 29, 31]
        self.al_better = ActivityList(self.problem, self.activities_order_better)
        self.schedule_better = ssgs.get_schedule(self.al_better)

    def test_update(self):
        rt = RTSystem(self.problem)
        rt.update(self.schedule)
        rt.update(self.schedule_better)
        self.assertGreater(len(rt.get_excluding_activities()), 0)


# class GARTHTestCase(unittest.TestCase):
#     def setUp(self):
#         parser = RCPParser()
#         self.problem_dict = parser(TEST_FILE)
#         self.problem = Problem(self.problem_dict)
#
#     def test_step(self):
#         g = GARTH(self.problem)
#         g.step()
#
#     def test_run(self):
#         g = GARTH(self.problem)
#         g.run()

