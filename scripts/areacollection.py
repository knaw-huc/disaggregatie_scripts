# -*- coding: utf-8 -*-
import collections

class AreaCollection:

    def __init__(self):
        self._area_coll = {}
        self._current_index = 0

    def __iter__(self):
        return self._area_coll.__iter__()

    def add_area(self,area):
        self._area_coll[area.get_area_code()] = area

    def add_census_to_area(self,area_code,census_code):
        if self.has_area(area_code):
            self.get_area(area_code).add_census_code(census_code)

    def get_area(self,area_code):
        return self._area_coll[area_code]

    def has_area(self,area_code):
        return area_code in self._area_coll

    def get_number_of_areas(self):
        return len(self._area_coll.keys())

    def items(self):
        return self._area_coll.items()

    def set_census_population(self,area_code,census_code,population_count):
        self._area_coll[area_code].set_census_population(census_code,population_count)

