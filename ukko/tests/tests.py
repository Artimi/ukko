import unittest
import nose

from ukko import RCPParser


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = RCPParser()
        self.result = self.parser('../../psplib/j30rcp/J301_1.RCP')

    def test_basic_info(self):
        self.assertEqual(self.result['num_activities'], 32)
        self.assertEqual(self.result['num_resources'], 4)
        self.assertListEqual(self.result['res_constraints'], [12, 13, 4, 12])

    def test_activities(self):
        activity = self.result['activities'][1]
        self.assertEqual(activity['duration'], 8)
        self.assertListEqual(activity['res_demands'], [4, 0, 0, 0])
        self.assertEqual(activity['num_successors'], 3)
        self.assertListEqual(activity['successors'], [6, 11, 15])
