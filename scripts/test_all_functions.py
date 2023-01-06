# -*- coding: utf-8 -*-
#from distances import calc_dist,find_year
from area import Area
from areacollection import AreaCollection
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
        self.assertEqual(res.get_number_of_areas(),12823)

    def test_read_links(self):
        inputdir = "Dummy_dataset_disaggregatie"
        f = f'{inputdir}/Dummy links.txt'
        areas,all_census,c,d = rw.create_link_dict(f)
        self.assertEqual(areas.get_number_of_areas(),1189)
        self.assertEqual(all_census.get_number_of_census(),5739)
        self.assertEqual(len(c),12)
        self.assertEqual(len(d),12)

    def test_read_census(self):
        inputdir = "Dummy_dataset_disaggregatie"
        header = 'BR1472a'
        inputfile = f'{inputdir}/census_{header}.txt'
        res = rw.read_census(inputfile)
        self.assertEqual(res.get_number_of_census(),610)

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
        self.assertEqual(a.get_area_code(),'X')
        self.assertEqual(a.get_surface(),1.0)
        self.assertEqual(f'{a}','area code: X - surface: 1.0')
        self.assertEqual(b.get_area_code(),'Z')
        self.assertEqual(b.get_surface(),2.0)
        self.assertEqual(f'{b}','area code: Z - surface: 2.0')

    def test_multiple_implementations(self):
        a = Area('X',1)
        b = Area('Z',2)
        a.add_census_code('BR0011')
        b.add_census_code('BR0012')
        self.assertEqual(len(a.get_census_list()),1)
        self.assertEqual(len(b.get_census_list()),1)

    def test_census_ready(self):
        a = Area('X',1)
        a.add_census_code('BR0011')
        a.add_census_code('BR0012')
        a.set_code_ready('BR0011')
        self.assertTrue(a.ready('BR0011'))
        self.assertFalse(a.ready('BR0012'))

class TestCensus(unittest.TestCase):

    def test_class_census(self):
        c = Census('xyz')
        c.set_counted(100)
        self.assertEqual(c.get_census_code(),'xyz')
        self.assertEqual(c.get_counted(),100.0)
        c.add_area('BR10000')
        self.assertEqual(c.get_areas(),['BR10000'])
        self.assertEqual(c.number_of_areas(),1)
        self.assertEqual(f'{c}',"census code: xyz - counted: 100.0 - areas: ['BR10000']")
        c.add_area('BR10000')
        self.assertEqual(c.number_of_areas(),1)
        c.add_area('BR10010')
        self.assertEqual(c.number_of_areas(),2)

class TestCensusCollection(unittest.TestCase):

    def test_class_censuscollection(self):
        c = CensusCollection()
        c.add_census(Census('xyz'))
        self.assertEqual(c.get_number_of_census(),1)
        self.assertTrue(isinstance(c.get_census('xyz'),Census))

class TestAreaCollection(unittest.TestCase):

    def test_class_areacollection(self):
        ac = AreaCollection()
        ac.add_area(Area('AB001',2.2))
        self.assertEqual(ac.get_number_of_areas(),1)
        self.assertTrue(ac.has_area('AB001'))


if __name__ == '__main__':
    unittest.main()

