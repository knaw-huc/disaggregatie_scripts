# -*- coding: utf-8 -*-

class Census:

    def __init__(self,census_code,area):
        self._census_code = census_code
        self._area = area

    def get_census_code(self):
        return self._census_code

    def get_area(self):
        return self._area

