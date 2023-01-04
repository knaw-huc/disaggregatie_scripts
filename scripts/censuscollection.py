# -*- coding: utf-8 -*-
import calculations as calc
from census import Census
import collections

class CensusCollection:

#    def __init__(self,census_coll_code):
    def __init__(self):
#        self._census_coll_code = census_coll_code
#        self._year = calc.find_year(census_coll_code)
        self._census_coll = collections.defaultdict(dict)

    def add_census(self,census):
        self._census_coll[census.get_census_code()] = census

#    def get_census_coll_code(self):
#        return self._census_coll_code

#    def get_year(self):
#        return self._year

    def get_census(self,census_code):
        return self._census_coll[census_code]

    def get_census_coll(self):
        return self._census_coll

    def has_census(self,census_code):
        return census_code in self._census_coll

    def get_number_of_census(self):
        return len(self._census_coll.keys())

    def __str__(self):
        return f"{self._census_coll_code} ({self._year})"
