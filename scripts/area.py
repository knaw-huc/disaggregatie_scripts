# -*- coding: utf-8 -*-
import census

class Area:

    area = ''
    surface = 0.0

    def __init__(self,area,surface,census_list=[]):
        self.area = area
        self.surface = float(surface)
        self.census_list = census_list

    def __str__(self):
        return f"{self.area}: {self.surface}"

    def add_census(self,census):
        self.census_list.append(census)

    def get_census_list(self):
        return self.census_list

    def get_area(self):
        return self.area

    def get_surface(self):
        return self.surface

    def set_surface(self,surface):
        self.surface = float(surface)

