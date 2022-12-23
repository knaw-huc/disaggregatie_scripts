# -*- coding: utf-8 -*-
from area import Area
import calculations as calc
import collections
import csv


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
    census = {}
    with open(inputfile, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        teller = 0
        for row in reader:
            try:
                census[row['UUID']] = float(row['PRIMARY_UNIT'])
            except:
                pass
    return census

def create_link_dict(f):
    year_header = {}
    kol = {}
    kol = collections.defaultdict(dict)
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for header in headers:
            if header!='SHORT_ID':
                year_header[calc.find_year(header)] = header
        years = sorted(year_header.keys())
        for year in years:
            kol[year] = []
        for row in reader:
            #areas.append(row['SHORT_ID'])
            for year in years:
                kol[year].append(row[year_header[year]])
    return year_header,years,kol


