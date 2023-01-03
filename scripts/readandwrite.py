# -*- coding: utf-8 -*-
from area import Area
import calculations as calc
from census import Census
from censuscollection import CensusCollection
import collections
import csv
import os.path


def read_surfaces(filename):
    areas = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            id = row['SHORT_ID']
            surface = row['KM2']
            areas[id] = Area(id,surface)
    return areas


def read_census(inputfile):
    basename = os.path.basename(inputfile).split('.')[0]
    coll_name = basename
    all_census = CensusCollection(coll_name)
    with open(inputfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        teller = 0
        for row in reader:
            all_census.add_census(Census(row['UUID'],float(row['PRIMARY_UNIT'])))
    return all_census

# aanpassen aan censuscollection
def create_link_dict(f):
    areas = []
    year_header = {}
    all_censuses = {}
    all_censuses = collections.defaultdict(dict)
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for header in headers:
            if header!='SHORT_ID':
                year_header[calc.find_year(header)] = header
        years = sorted(year_header.keys())
        for year in years:
            all_censuses[year] = []
        for row in reader:
            area = row['SHORT_ID']
            areas.append(area)
            for year in years:
                census_code = row[year_header[year]]
                all_censuses[year].append(Census(census_code,area))
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

