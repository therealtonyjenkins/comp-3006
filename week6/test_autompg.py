"""Unit tests for the autompg program."""
import unittest

from autompg import *

class TestAutoMPG(unittest.TestCase):

    def test_init(self):
        a1 = AutoMPG(1, 2, 3, 4)
        self.assertEqual("1", a1.make)
        self.assertEqual("2", a1.model)
        self.assertEqual(1903, a1.year)
        self.assertEqual(4.0, a1.mpg)

    def test_eq(self):
        # test when they are equal
        a1 = AutoMPG('a', 'b', 3, 4)
        a2 = AutoMPG('a', 'b', 3, 4)
        self.assertTrue(a1 == a2)
        self.assertFalse(a1 != a2)

        # test each attribute
        a2 = AutoMPG('c', 'b', 3, 4)
        self.assertTrue(a1 != a2)
        self.assertFalse(a1 == a2)

        a2 = AutoMPG('a', 'c', 3, 4)
        self.assertTrue(a1 != a2)
        self.assertFalse(a1 == a2)
        
        a2 = AutoMPG('a', 'b', 0, 4)
        self.assertTrue(a1 != a2)
        self.assertFalse(a1 == a2)
        
        a2 = AutoMPG('a', 'b', 3, 0)
        self.assertTrue(a1 != a2)
        self.assertFalse(a1 == a2)
        
    def test_hash(self):
        a1 = AutoMPG('a', 'b', 3, 4)
        a2 = AutoMPG('a', 'b', 3, 4)

        # sets will only have unique values - determined by hash
        s = {a1, a2}
        self.assertEqual(1, len(s))
        self.assertTrue(a1 in s)
        self.assertTrue(a2 in s)

        # now make sure each attribute is considered in the
        # has function
        b1 = AutoMPG('c', 'b', 3, 4)
        s.add(b1)
        self.assertEqual(2, len(s))
        self.assertTrue(b1 in s)
                
        b1 = AutoMPG('a', 'c', 3, 4)
        s.add(b1)
        self.assertEqual(3, len(s))
        self.assertTrue(b1 in s)
                
        b1 = AutoMPG('a', 'b', 0, 4)
        s.add(b1)
        self.assertEqual(4, len(s))
        self.assertTrue(b1 in s)

        b1 = AutoMPG('a', 'b', 3, 0)
        s.add(b1)
        self.assertEqual(5, len(s))
        self.assertTrue(b1 in s)
                
    @unittest.expectedFailure
    def test_lt_wrong_type(self):
        a1 = AutoMPG('a', 'b', 3, 4)
        a1 < "should not work"

    def test_lt_mpg(self):
        a1 = AutoMPG('a', 'b', 3, 4)
        a2 = AutoMPG('a', 'b', 3, 5)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_lt_year(self):
        a1 = AutoMPG('a', 'b', 3, 0)
        a2 = AutoMPG('a', 'b', 4, 0)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_lt_model(self):
        # make, model, year are the only ones that matter
        a1 = AutoMPG('a', 'b', 0, 0)
        a2 = AutoMPG('a', 'c', 0, 0)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_lt_make(self):
        # make, model, year are the only ones that matter
        a1 = AutoMPG('a', 'c', 0, 0)
        a2 = AutoMPG('b', 'c', 0, 0)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

class TestAutoMPGData(unittest.TestCase):

    def test_iterable(self):
        # make sure it is possible to get and iterator from AutoMPGData
        iter(AutoMPGData())
                
if __name__ == '__main__':
    unittest.main()

