# -*- coding: utf-8 -*-
import census

class Area:

    area = ''
    surface = 0.0

    def __init__(self,area,surface=0.0,census_list=[]):
        self._area = area
        self._surface = float(surface)
        self._census_list = census_list

    def __str__(self):
        return f"{self._area}: {self._surface}"

    def add_census(self,census):
        self._census_list.append(census)

    def get_census_list(self):
        return self._census_list

    def get_area(self):
        return self._area

    def get_surface(self):
        return self._surface

    def set_surface(self,surface):
        self._surface = float(surface)
    
