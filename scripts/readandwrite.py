# -*- coding: utf-8 -*-
from area import Area
from areacollection import AreaCollection
import calculations as calc
from census import Census
from censuscollection import CensusCollection
import collections
import csv
import os.path


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


def read_census(inputfile,all_census = CensusCollection()):
    basename = os.path.basename(inputfile).split('.')[0]
    #coll_name = basename
    #all_census = CensusCollection(coll_name)
    with open(inputfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        teller = 0
        for row in reader:
            all_census.add_census(Census(row['UUID'],float(row['PRIMARY_UNIT'])))
    return all_census


def create_link_dict(f):
    areas = AreaCollection()
    year_header = {}
    all_censuses = CensusCollection()
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        #headers.remove('SHORT_ID')
        for header in headers:
            if header!='SHORT_ID':
                year_header[calc.find_year(header)] = header
        years = sorted(year_header.keys())
#        for year in years:
#            all_censuses = CensusCollection(year_header[year])
        for row in reader:
            area_id = row['SHORT_ID']
            area = Area(area_id)
            areas.add_area(area)
            for col_head in headers:
                if col_head!='SHORT_ID':
                    census_code = row[col_head]
                    if census_code != '':
                        areas.add_census_to_area(area_id,census_code)
                        if all_censuses.has_census(census_code):
                            census = all_censuses.get_census(census_code)
                        else:
                            census = Census(census_code,0)
                        census.add_area(area_id)
                        all_censuses.add_census(census)
    return areas,all_censuses,year_header,years


def make_xlsx(columns,data,new_res,uitvoer='default.xlsx',small=False):
    # if uitvoer=='default.xlsx':
    #   add date_time
    new_rows = []
    for k,v in new_res.items():
        new_row = [k]
        new_row.append(v['surface'])
        for year in years:
            try:
                new_row.append(v[year]['number'])
                if not small:
                    new_row.append(v[year]['status'])
                    new_row.append(v[year]['census'])
                    try:
                        new_row.append(v[year]['orig'])
                    except:
                        new_row.append('')
            except:
                new_row.append('')
                if not small:
                    new_row.append('')
                    new_row.append('')
                    new_row.append('')
        new_rows.append(new_row)
    columns = ['Area','km2']
    for year in years:
        columns.append(f'{year_header[year]}')
        if not small:
            columns.append(f'stat')
            columns.append(f'census')
            columns.append(f'orig')
    print(len(columns))
    print(len(new_rows[0]))
    print(new_rows[0])
    new_df = pd.DataFrame(new_rows, columns=columns)
    new_df.to_excel(uitvoer)

