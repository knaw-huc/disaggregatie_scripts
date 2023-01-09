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

    def get_all_from_census_id(self,census_id):
        res = []
        for census_code in self._census_coll.keys():
            census = self.get_census(census_code)
            if census.get_census_id() == census_id:
                res.append(census)
        return res

    def get_census_coll(self):
        return self._census_coll

    def has_census(self,census_code):
        return census_code in self._census_coll

    def get_number_of_census(self):
        return len(self._census_coll.keys())

    def get_max_areas(self):
        res = 0
        for census_code in self._census_coll.keys():
            num_areas = self.get_census(census_code).number_of_areas()
            if num_areas>res:
                res = num_areas
        return res

    def get_number_ready(self, census_id, areas):
        res = 0.0
        count_ready = 0.0
        count_all = 0.0
        for census in self.get_all_from_census_id(census_id):
            c_areas = census.get_areas()
            for a in c_areas:
                area = areas.get_area(a)
                if area.ready(census.get_census_code()):
                    count_ready += 1
                count_all += 1
        res = count_ready * 100 / count_all
        return res

