# -*- coding: utf-8 -*-

class Census:

    def __init__(self,census_code,counted):
        self._census_code = census_code
        self._counted = float(counted)
        self._areas = []

    def get_census_code(self):
        return self._census_code

    def get_areas(self):
        return self._areas

    def add_area(self,area):
        self._areas.append(area)

    def has_area(self,area_code):
        return area_code in self._areas

    def get_counted(self):
        return self._counted

    def __str__(self):
        return f"census code: {self._census_code} -  counted: {self._counted} - areas: {self._areas}"

