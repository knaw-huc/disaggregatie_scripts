# -*- coding: utf-8 -*-

class Census:

    def __init__(self,census_code,population,areas = []):
        self._census_code = census_code
        self._population = population
        if isinstance(areas,list):
            self._areas = areas
        else:
            self._areas = [areas]

    def get_census_code(self):
        return self._census_code

    def get_areas(self):
        return self._areas

    def add_area(self,area):
        self._areas.append(area)

    def has_area(self,area_code):
        return area_code in self._areas

    def get_population(self):
        return self._population

    def __str__(self):
        return f"{self._census_code} - {self._population} - {self._areas}"

