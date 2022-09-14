# -*- coding: utf-8 -*-
import csv
#import json
#import psycopg2
#from config import config
from collections import Counter
import collections
from datetime import datetime
import glob
import math
import numpy as np
import os.path
import re
import sys
import pandas as pd
import pprint as pp

# global variables
all_data = {}
census_list = {}
surfaces = {}
id_census = {}
census_id = {}
new_res = collections.defaultdict(dict)


def create_link_dict(f):
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for row in reader:
            short_id = row['SHORT_ID']
            id_census[short_id] = []
            for key in headers:
                if key!='SHORT_ID' and row[key]!='':
                    if row[key] in census_id:
                        census_id[row[key]].append(short_id)
                    else:
                        census_id[row[key]] = [short_id]
                    id_census[short_id].append(row[key])
    #print('id_census:') 
    #pp.pprint(id_census)
    #print('\n\ncensus_id:') 
    #pp.pprint(census_id)
    #print('\n')
    return


def get_data(year,cell):
    df = all_data[census_list[year]]
    res = df.loc[df['UUID'] == cell]
    try:
        res = res.iloc[0]['PRIMARY_UNIT']
    except Exception as err:
        if not isinstance(cell, str) and math.isnan(cell):
            return cell
        stderr(f'year: {year}')
        stderr(f'cell: {cell}')
        stderr(f'err: {err}')
        end_prog(1)
    return res


def calculate(a,b,c):
    return (a * b) / c


def split_on_area(census,areas):
    #stderr(f'census: {census} - areas: {areas}')
    year = get_year(census)
    #stderr(f'year: {year}')
    tot_area = 0.0
    census_value = get_census_value(census)
    for a in areas:
        tot_area += surfaces[a]
    #stderr(f'tot area: {tot_area}')
    for i in range(len(areas)):
        surf = surfaces[areas[i]]
        #stderr(f'surf: {surf}')
        new_val = calculate(census_value, surf, tot_area)
        #stderr(f'new_val: {new_val}')
        add_value(areas[i],year,new_val)

def split_population(census,cc,areas):
    #stderr(f'census: {census} - cc: {cc} - areas: {areas}')
    year = get_year(census)
    #stderr(f'year: {year}')
    val = get_census_value(census)
    #stderr(f'val: {val}')
    ref_total = 0
    for c in cc:
        ref_total += get_census_value(c)
    #stderr(f'ref_total: {ref_total}')
    for i in range(len(areas)):
        new_val = calculate(val,get_census_value(cc[i]),ref_total)
        #stderr(f'new_val: {new_val}')
        add_value(areas[i],year,new_val)

def remainder():
    for census,areas in census_id.items():
        year = get_year(census)
        for area in areas:
            try:
                exists = new_res[area][year]
            except:
                #stderr(f'calculate: {area} - {year}')
                split_on_area(census,areas)
                break



def add_value(area,year,val):
    try:
        old_val = new_res[area][year]
        stderr(f'exists? {area} {year} {val}')
        stderr(f'this should not happen')
        exit(1)
    except:
        new_res[area][year] = val


def get_year(k):
    year = re.search(r'(\d\d\d\d)',k).group(1)
    return year


def get_census_value(census):
    year = get_year(census)
    val = get_data(year,census)
    return val


def recalc(area_num):
    for k,v in census_id.items():
        if len(v)==area_num:
            count = 0
            area_split = 0
            cc = []
            for c in v:
                for c2 in id_census[c]:
                    if c2!=k:
                        if len(census_id[c2])==1:
                            count +=1
                            cc.append(c2)
                        elif len(census_id[c2])==area_num:
                            area_split +=1
                    else:
                        area_split += 1
            if count==area_num:
                split_population(k,cc,v)
            elif area_split==area_num:
                split_on_area(k,v)


def make_excel(table,output='test_res_7.xlsx'):
    new_df = pd.DataFrame(table, columns=['Code'] + years)
    new_df.to_excel(output)


def end_prog(code=0):
    if code!=0:
        code_str = f' (met code {code})'
    else:
        code_str = ''
    stderr(datetime.today().strftime(f"einde: %H:%M:%S{code_str}"))
    sys.exit(code)


def stderr(text,nl='\n'):
    sys.stderr.write(f"{text}{nl}")


if __name__ == '__main__':
    stderr(datetime.today().strftime("start: %H:%M:%S"))

    inputdir = "Dummy_dataset_disaggregatie"

    all_files = glob.glob(f"{inputdir}/census_*.txt")

    for f in all_files:
        basename = os.path.basename(f).replace('census_','').replace('.txt','')
        year = re.search(r'(\d\d\d\d)',basename).group(1)
        try:
            df = pd.read_csv(f, sep='\t', usecols=['UUID', 'YEAR', 'PRIMARY_UNIT'])
            if True:
                all_data[basename] = df
                census_list[year] = basename
        except ValueError as vErr:
            basename = os.path.basename(f).replace('txt','xlsx')
            stderr(basename)
            df = pd.read_csv(f, sep='\t')
            df.to_excel(basename)
            stderr(vErr)
            stderr(f)
    years = sorted(census_list.keys())

    f = f'{inputdir}/Dummy km2.txt'
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            surfaces[row['SHORT_ID']] = float(row['KM2'])

    f = f'{inputdir}/Dummy links.txt'
    links = pd.read_csv(f, sep='\t')
    links_cols = links.columns

    f = f'{inputdir}/Dummy links.txt'
    create_link_dict(f)

#   the simple things: just one value on one area
    for k,v in census_id.items():
        if len(v)==1:
            val = get_census_value(k)
            add_value(v[0],get_year(k),val)

    res = max(len(elem) for elem in census_id.values())

#   two or more areas
    for area_num in range(2,res+1):
        recalc(area_num)

    # calculate remainder on basis of surface
    remainder()

#    print('\n')
#    pp.pprint(new_res)

    build_table = []
    for key in id_census.keys():
        new_row = [key]
        if not key in new_res.keys():
            build_table.append(new_row)
            continue
        for year in years:
            if year in new_res[key]:
                new_row.append(new_res[key][year])
            else:
                new_row.append(' ')
        build_table.append(new_row)

    make_excel(build_table)
    new_df = pd.DataFrame(build_table, columns=['Code'] + years)
    new_df.to_excel('test_res_8.xlsx')

    end_prog(0)

