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
def build_matrix(areas,years,all_census,compact=True):
    result = []
    for area_code in areas:
        area = areas.get_area(area_code)
        if area.has_census_list():
            cl = area.get_census_list()
            if compact:
                row = [''] * (2 + len(years))
            else:
                row = [''] * (2 + 3 * len(years))
            row[0] = area_code
            row[1] = area.get_surface()
            for census_code in cl:
                year = find_year(census_code)
                if compact:
                    idx = years.index(year)
                    row[idx+2] = area.get_census_population(census_code)
                else:
                    idx = 3 * years.index(year)
                    row[idx+2] = area.get_census_population(census_code)
                    row[idx+3] = census_code
                    row[idx+4] = all_census.get_census(census_code).get_counted()
                if not compact:
                    pass
            result.append(row)
    return result


def stderr(text,nl='\n'):
    sys.stderr.write(f"{text}{nl}")

# calculate the population spread of a census on the areas it contains,
# based on the values of an other year, where the values are already determined,
# either by a previous calculation, or an initial count.
def calc_population_spread(all_census,areas,ready_c_s,census,debug=False):
    num_of_areas = len(ready_c_s)
    census_code = census.get_census_code()
    if debug:
        stderr('start calculating:')
        stderr(f'{ready_c_s} can be used to calculate')
        stderr(f'areas {census.get_areas()} in {census_code}')
    census_id = census.get_census_id()
    counted = census.get_counted()
    c_1_tot_population = 0.0
    area_pop_known = {}
    for c_1 in list(set(ready_c_s)):
        c_2 = all_census.get_census(c_1)
        #c_2_id = c_2.get_census_id()
        for a_1 in c_2.get_areas():
            a_2 = areas.get_area(a_1)
            if a_1 in census.get_areas():
                if debug:
                    stderr(f'{a_1}: {a_2.get_census_population(c_1)}')
                area_pop_known[a_1] = a_2.get_census_population(c_1)
                c_1_tot_population += a_2.get_census_population(c_1)
    if debug:
        stderr(area_pop_known)
        stderr(c_1_tot_population)
        stderr(f'census: {counted}')
    for a in census.get_areas():
        res = counted * area_pop_known[a] / c_1_tot_population
        if debug:
            stderr(f'a: {a}')
            stderr(f'res: {res}')
        area = areas.get_area(a)
        area.set_census_population(census_code,res)
        area.set_code_ready(census_code)


# calculate populations for a specific census-'year' based on the area surfaces
def calculate_using_surface(census_id,all_census,areas):
    census_list = all_census.get_all_from_census_id(census_id)
    for census in census_list:
        census_code = census.get_census_code()
        census_areas = census.get_areas()
        te_doen = []
        for area_code in census_areas:
            area = areas.get_area(area_code)
            if not area.ready(census_code):
                te_doen.append(area)
        if len(te_doen)>0:
            tot_surface = 0.0
            for area in te_doen:
                tot_surface += area.get_surface()
            for area in te_doen:
                res = census.get_counted() * area.get_surface() / tot_surface
                area.set_census_population(census_code,res)
                area.set_code_ready(census_code)


