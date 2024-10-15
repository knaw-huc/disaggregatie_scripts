# -*- coding: utf-8 -*-
from area import Area
from areacollection import AreaCollection
import calculations as calc
from census import Census
from censuscollection import CensusCollection
import collections
import csv
import os.path
import pandas as pd


def read_surfaces(filename,areas=AreaCollection()):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            id = row['SHORT_ID']
            surface = row['KM2']
            if areas.has_area(id):
                areas.get_area(id).set_surface(surface)
            else:
                # the file with areas and their surface contains much more
                # areas than the other files
                areas.add_area(Area(id,surface))
    return areas


def read_census(inputfile, uid, census_id_header, year_header, primary_unit,
        all_census=CensusCollection(), debug=False):
    with open(inputfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            census_code = row[uid]
            census_id = row[census_id_header]
            try:
                counted = float(row[primary_unit])
                year = row[year_header]
                if not all_census.has_census(census_code):
                    census = Census(census_code)
                    census.set_census_id(census_id)
                    census.set_counted(counted)
                    census.set_year(year)
                    all_census.add_census(census)
                else:
                    # if census exists there is something funny going on
                    census = all_census.get_census(census_code)
                    print(f'twice in all_census? : {census}')
            except ValueError as e:
                if debug:
                    print(f'census_code: {census_code}')
                    print(f'error: {e}')
                # census has no value filled in:
                # there was no census for this area in this year:
                # ignore
                pass
    return all_census


def create_link_dict(f,all_census=CensusCollection(),debug=False):
    areas = AreaCollection()
    year_header = {}
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for header in headers:
            if header!='SHORT_ID':
                year_header[calc.find_year(header)] = header
       years = sorted(year_header.keys())
        for row in reader:
            area_id = row['SHORT_ID']
            area = Area(area_id)
            areas.add_area(area)
            for col_head in headers:
                if col_head!='SHORT_ID':
                    census_code = row[col_head]
                    if census_code and census_code != '':
                        if all_census.has_census(census_code):
                            areas.add_census_to_area(area_id,census_code)
                            census = all_census.get_census(census_code)
                            census.add_area(area_id)
    return areas,all_census,year_header,years


def make_xlsx(columns,data,uitvoer='default.xlsx',small=False):
#    print(len(columns))
#    print(len(data[0]))
#    print(data[0])
    new_df = pd.DataFrame(data, columns=columns)
    new_df.to_excel(uitvoer)

