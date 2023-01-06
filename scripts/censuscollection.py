# -*- coding: utf-8 -*-
import calculations as calc
from census import Census
import collections

class CensusCollection:

    def __init__(self):
        self._census_coll = collections.defaultdict(dict)

    def __iter__(self):
        return self._census_coll.__iter__()

    def add_census(self,census):
        self._census_coll[census.get_census_code()] = census

    def remove_census(self,census):
        self._census_coll.pop(census.get_census_code())

    def get_census(self,census_code):
        return self._census_coll[census_code]

    def get_census_coll(self):
        return self._census_coll

    def has_census(self,census_code):
        return census_code in self._census_coll

    def get_number_of_census(self):
        return len(self._census_coll.keys())

