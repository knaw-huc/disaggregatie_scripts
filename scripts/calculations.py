# -*- coding: utf-8 -*-
import re


def find_year(census):
    return int(re.search(r'\d{4}',census).group(0))

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
    cl = all_census.get_census_coll()
    for census_code in cl:
        census = cl[census_code]
        counted = census.get_counted()
        if census.number_of_areas()==1:
            area_code = census.get_areas()[0]
            area = areas.get_area(area_code)
            area.set_census_population(census_code,counted)
            area.set_code_ready(census_code)


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

