#!/usr/bin/python

import random
import unittest

import mod20q as tq

class TestSimilarity(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)
        self.trail = '-9n-10y-15n-1y'
        self.similar_trail = '-1y-2y-10y-11n-15n'
        self.dissimilar_trail = '-9y-10n-11n-12y-15n'
        self.resp        = tq.trail_to_responses(self.trail)
        #1 Do you live in Seattle?
        #2 Do you live in the United States?
        #3 Do you live in Europe?
        #4 Do you smoke?
        self.correlation_trails = [
            '-1y-2y-3n-4y', #I live in Seattle, I smoke
            '-1y-2y-4n', #I live in Seattle, I don't smoke
            '-1n-2y-3n-4y', #I live in New York and smoke
            '-1n-2y-3n-4n', #I live in New York and don't smoke
            '-1n-2n-3y-4y', #I live in London and smoke
            '-1n-2n-3y-4n', #I live in London and don't smoke
            '-1n-2n-3n-4y', #I live in Tokyo
            '-1n-2n-3n-4n', #I live in Tokyo
            '-1y-3n-4n', #I live in Seattle, I don't smoke
            ]

        self.correlation_things = [ 
            tq.make_thing('Foo', tr) for tr in self.correlation_trails ]

    def test_tuple_list(self):
        trail_list = tq.trail_to_tuple_list(self.trail)
        expected = [('9', 'n'), ('10', 'y'), ('15', 'n'), ('1', 'y')]
        self.assertEqual(trail_list, expected)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_similarity_high(self): 
        self.resp_sim = tq.trail_to_responses(self.similar_trail)
        sim = tq.similarity(self.resp, self.resp_sim)
        self.assertEqual(sim, 1.0)

    def test_similarity_low(self):
        self.resp_dissim = tq.trail_to_responses(self.dissimilar_trail)
        sim = tq.similarity(self.resp, self.resp_dissim)
        self.assertEqual(sim, 1.0/3)

    def test_similarity_zero_num(self):
        sim = tq.similarity(self.resp, { '9':'y', '10':'n'})
        self.assertEqual(sim, 0.0)

    def test_similarity_zero_denom(self):
        sim = tq.similarity(self.resp, { '4444':'y'})
        self.assertEqual(sim, 0)

    def test_correlation_implies(self):
        #If 1, then 2, If you live in Seattle, you live in the US
        cor = tq.correlation('1', '2', self.correlation_things )
        self.assertEqual(cor, 1.0)

    def test_correlation_implies_not(self):
        #If 2, then not 2, If you live in the US, you do not live in Europe
        cor = tq.correlation('2', '3', self.correlation_things )
        self.assertEqual(cor, -1.0)

    def test_correlation_unrelated(self):
        #If 2, then neither necessarily 4 nor not 4, If you live in the Seattle, you might smoke
        cor = tq.correlation('2', '4', self.correlation_things )
        self.assertTrue(cor != 1.0 and cor != -1.0 and abs(cor) <= 1)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

if __name__ == '__main__':
    unittest.main()
