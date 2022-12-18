# -*- coding: utf-8 -*-
import csv
import collections
from distances import find_year


areas = []
year_header = {}
years = []

def get_areas():
    return areas

def get_year_header():
    return year_header

def get_years():
    return years

def create_link_dict(f):
    global areas, year_header, years
    kol = collections.defaultdict(dict)
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for header in headers:
            if header!='SHORT_ID':
                year_header[find_year(header)] = header
        years = sorted(year_header.keys())
        for year in years:
            kol[year] = []
        for row in reader:
#            if row['SHORT_ID'].startswith('BR0010'):
                areas.append(row['SHORT_ID'])
                for year in years:
                    kol[year].append(row[year_header[year]])
    return True
#    return areas,kol,year_header,years


