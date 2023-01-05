# -*- coding: utf-8 -*-
import census

class Area:

    def __init__(self,area_code,surface=0.0,census_list=[]):
        self._area_code = area_code
        self._surface = float(surface)
        self._census_list = []
        self._ready = {}
        for c in census_list:
            self._census_list.append(c)
            self._ready[c] = False
        self._census_population = {}

    def __str__(self):
        return f"area code: {self._area_code} - surface: {self._surface}"

    def get_area_code(self):
        return self._area_code

    def get_surface(self):
        return self._surface

    def set_surface(self,surface):
        self._surface = float(surface)

    def add_census_code(self,census_code):
        if not census_code in self._census_list:
            self._census_list.append(census_code)
            self._ready[census_code] = False

    def get_census_list(self):
        return self._census_list

    def has_census_list(self):
        return len(self._census_list)>0

    def get_census_population(self,census_code):
        try:
            return self._census_population[census_code]
        except:
            return ''

    def set_census_population(self,census_code,population_count):
        self._census_population[census_code] = population_count

    def set_code_ready(self,census_code):
        self._ready[census_code] = True

    def ready(self,census_code):
        try:
            return self._ready[census_code]
        except:
            return False
