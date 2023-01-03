# -*- coding: utf-8 -*-
#from distances import calc_dist,find_year
from area import Area
import calculations as calc
from census import Census
from censuscollection import CensusCollection
import readandwrite as rw
import pprint as pp
import unittest

class TestReadWrite(unittest.TestCase):

    def test_read_surfaces(self):
        inputdir = "Dummy_dataset_disaggregatie"
        f = f'{inputdir}/Dummy km2.txt'
        res = rw.read_surfaces(f)
        self.assertEqual(len(res),12823)

    def test_read_links(self):
        inputdir = "Dummy_dataset_disaggregatie"
        f = f'{inputdir}/Dummy links.txt'
        a,b,c,d = rw.create_link_dict(f)
        self.assertEqual(len(a),1189)
        self.assertEqual(len(b),12)
        self.assertEqual(len(c),12)
        self.assertEqual(len(d),12)

    def test_read_census(self):
        inputdir = "Dummy_dataset_disaggregatie"
        header = 'BR1374a'
        inputfile = f'{inputdir}/census_{header}.txt'
        res = rw.read_census(inputfile)
        self.assertEqual(res.getNumberOfCensus(),617)

class TestCalculations(unittest.TestCase):

    def test_distances(self):
        res = calc.calc_dist(['BR1374a','BR1437a','BR1464a','BR1468a','BR1472a','BR1480a','BR1492a','BR1496a','BR1526a','ME1544a','NED1795a','BEL1800a'])
        self.assertEqual(len(res),12)
        self.assertEqual(res['BR1374a'][0],'BR1437a')

    def test_get_year(self):
        res = calc.find_year('BR1496a')
        self.assertEqual(res,1496)

class TestArea(unittest.TestCase):

    def test_class_area(self):
        a = Area('X',1)
        b = Area('Z',2)
        self.assertEqual(a.get_area(),'X')
        self.assertEqual(a.get_surface(),1.0)
        self.assertEqual(b.get_area(),'Z')
        self.assertEqual(b.get_surface(),2.0)

class TestCensus(unittest.TestCase):

    def test_class_census(self):
        c = Census('xyz',100,'BR10000')
        self.assertEqual(c.get_census_code(),'xyz')
        self.assertEqual(c.get_areas(),['BR10000'])
        self.assertEqual(c.get_population(),100)

class TestCensusCollection(unittest.TestCase):

    def test_class_censuscollection(self):
        c = CensusCollection('XY-1456a')
        c.add_census(Census('xyz',22,'BB101'))
        self.assertEqual(c.getNumberOfCensus(),1)


if __name__ == '__main__':
    unittest.main()

