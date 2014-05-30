#!/usr/bin/python

import random
import unittest

import mod20q as tq

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)
        self.trail = '-9n-10y-15n-1y'

    def test_tuple_list(self):
        trail_list = tq.as_tuple_list(self.trail)
        expected = [('9', 'n'), ('10', 'y'), ('15', 'n'), ('1', 'y')]
        self.assertEqual(trail_list, expected)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()
