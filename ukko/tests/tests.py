import unittest
import nose

from ukko import RCPParser, Problem,  ActivityList

TEST_FILE = '../../psplib/j30rcp/J301_1.RCP'


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = RCPParser()
        self.result = self.parser(TEST_FILE)

    def test_basic_info(self):
        self.assertEqual(self.result['num_activities'], 32)
        self.assertEqual(self.result['num_resources'], 4)
        self.assertListEqual(self.result['res_constraints'], [12, 13, 4, 12])

    def test_activities(self):
        activity = self.result['activities']
        self.assertEqual(activity['duration'][1], 8)
        self.assertListEqual(activity['res_demands'][1], [4, 0, 0, 0])
        # self.assertEqual(activity['num_successors'], 3)
        # self.assertListEqual(activity['successors'], [5, 10, 14])


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

