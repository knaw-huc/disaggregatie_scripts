# -*- coding: utf-8 -*-

class Census:

    def __init__(self,census_code,area,area_name=''):
        self._census_code = census_code
        self._area = area
        self._area_name = area_name

    def get_census_code(self):
        return self._census_code

    def get_area(self):
        return self._area

    def get_area_name(self):
        return this._area_name

    def set_area_name(self,area_name):
        this._area_name = area_name

