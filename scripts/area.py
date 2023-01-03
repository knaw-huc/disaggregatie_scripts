# -*- coding: utf-8 -*-
import census

class Area:

    def __init__(self,area_code,surface=0.0,population=0.0,census_list=[]):
        self._area_code = area_code
        self._surface = float(surface)
        self._population = float(population)
        self._census_list = []
        for c in census_list:
            self._census_list.append(c)
        self._census_population = {}

    def __str__(self):
        return f"area code: {self._area_code} - surface: {self._surface} - population: {self._population}"

    def add_census_code(self,census_code):
        if not census_code in self._census_list:
            self._census_list.append(census_code)

    def get_area_code(self):
        return self._area_code

    def get_census_list(self):
        return self._census_list

    def get_census_population(self):
        return self._census_population

    def get_population(self):
        return self._population

    def get_surface(self):
        return self._surface

    def set_census_population(self,census_code,population_count):
        self._census_population[census_code] = population_count

    def set_population(self,population):
        self._population = population

    def set_surface(self,surface):
        self._surface = float(surface)
    
