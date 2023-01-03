# -*- coding: utf-8 -*-
import calculations as calc
import collections

class CensusCollection:

    def __init__(self,census_coll_code):
        self._census_coll_code = census_coll_code
        self._year = calc.find_year(census_coll_code)
        self._census_coll = collections.defaultdict(dict)

    def add_census(self,census):
        self._census_coll[census.get_census_code()] = census

    def get_census_code(self):
        return self._census_code

    def get_year(self):
        return self._year

    def get_census(self,census_code):
        return _censes_coll[census_code]

    def has_census(self,census_code):
        return census_code in self._census_coll

    def getNumberOfCensus(self):
        return len(self._census_coll)

    def __str__(self):
        return f"{self._census_code} ({self._year})"
