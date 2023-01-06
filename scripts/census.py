# -*- coding: utf-8 -*-

class Census:

    def __init__(self,census_code):
        self._census_code = census_code
        self._areas = []

    def get_census_id(self):
        return self._census_id

    def set_census_id(self,census_id):
        self._census_id = census_id

    def get_census_code(self):
        return self._census_code

    def add_area(self,area_code):
        if area_code not in self._areas:
            self._areas.append(area_code)

    def get_areas(self):
        return self._areas

    def has_area(self,area_code):
        return area_code in self._areas

    def number_of_areas(self):
        return len(self._areas)

    def get_counted(self):
        try:
            return self._counted
        except:
            return ''

    def set_counted(self,counted):
        self._counted = float(counted)

    def __str__(self):
        return f"census code: {self._census_code} - counted: {self.get_counted()} - areas: {self._areas}"

