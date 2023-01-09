# -*- coding: utf-8 -*-
import re
import sys


def find_year(census):
    return int(re.search(r'\d{4}',census).group(0))


#
def calc_dist(years):
    result = {}
    for year in years:
        result[year] = []
        y1 = find_year(year)
        for y2 in years:
            if y2!=year:
                y3 = find_year(y2)
                result[year].append((abs(y1-y3),y2))
            result[year] = sorted(result[year])
    res = {}
    for (k,v) in iter(result.items()):
        res[k] = []
        for y in v:
            res[k].append(y[1])
    return res


# fill in the population values for all the area/year pairs which don't have a 'shared census';
# i.e. a census that only counted that area in a perticular year
def fill_single_values(all_census,areas):
    for census_code in all_census:
        census = all_census.get_census(census_code)
        try:
            counted = census.get_counted()
            if census.number_of_areas()==1:
                area_code = census.get_areas()[0]
                area = areas.get_area(area_code)
                area.set_census_population(census_code,counted)
                area.set_code_ready(census_code)
        except:
            # empty census
            pass


# the result matrix is used to write data to an xlsx
def build_matrix(areas,years):
    result = []
    for area_code in areas:
        area = areas.get_area(area_code)
        if area.has_census_list():
            cl = area.get_census_list()
            row = [''] * (2 + len(years))
            row[0] = area_code
            row[1] = area.get_surface()
            for census_code in cl:
                year = find_year(census_code)
                idx = years.index(year)
                row[idx+2] = area.get_census_population(census_code)
            result.append(row)
    return result

# calculate the population spread of a census on the areas it contains,
# based on the values of an other year, where the values are already determined,
# either by a previous calculation, or an initial count.
def calc_population_spread(all_census,areas,ready_c_s,census):
    num_of_areas = len(ready_c_s)
    census_code = census.get_census_code()
    census_id = census.get_census_id()
    counted = census.get_counted()
    c_1_tot_population = 0.0
    area_pop_known = {}
    for c_1 in ready_c_s:
        c_2 = all_census.get_census(c_1)
        for a_1 in c_2.get_areas():
            a_2 = areas.get_area(a_1)
            area_pop_known[a_1] = a_2.get_census_population(c_1)
            c_1_tot_population += a_2.get_census_population(c_1)
    for a in census.get_areas():
        res = counted * area_pop_known[a] / c_1_tot_population
        area = areas.get_area(a)
        area.set_census_population(census_code,res)
        area.set_code_ready(census_code)

