# -*- coding: utf-8 -*-
import csv
import collections
from datetime import datetime
import glob
import math
import os.path
import pandas as pd
import pprint as pp
import re
import sys


def get_year(k):
    year = re.search(r'(\d\d\d\d)',k).group(1)
    return year

def create_link_dict(f):
    areas = []
    year_header = {}
    years = []
    kol = collections.defaultdict(dict)
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        headers = reader.fieldnames
        for header in headers:
            if header!='SHORT_ID':
                year_header[get_year(header)] = header
        years = sorted(year_header.keys())
        for year in years:
            kol[year] = []
        for row in reader:
            areas.append(row['SHORT_ID'])
            for year in years:
                kol[year].append(row[year_header[year]])
    return areas,kol,year_header,years


def get_census(inputdir):
    all_files = glob.glob(f"{inputdir}/census_*.txt")
    census = {}
    for f in all_files:
        with open(f, newline='') as csvfile:
            reader = csv.DictReader(csvfile,delimiter='\t')
            teller = 0
            for row in reader:
                try:
                    census[row['UUID']] = float(row['PRIMARY_UNIT'])
                except:
                    pass
    return census


def get_km(inputdir):
    f = f'{inputdir}/Dummy km2.txt'
    surfaces = {}
    with open(f, newline='') as csvfile:
        reader = csv.DictReader(csvfile,delimiter='\t')
        for row in reader:
            surfaces[row['SHORT_ID']] = float(row['KM2'])
    return surfaces


def find_all(new_res,year,census,debug=False):
    if debug:
        stderr(f'find_all: {year}, {census}')
    result = []
    for area in new_res:
        if new_res[area][year]['census']==census:
            result.append(area)
    return result



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

#    new_res = collections.defaultdict(dict)
    '''
    areas = ['a01','a02','a03','a04','a05','a06', 'a07', 'a08', 'a09', 'a10', 'a11', 'a12']
    km2s = []

    kol = {'1': ['c1','c1','c1','c1','c1','c1','c1','c1','c1','c1','c21','c21'] ,
            '2': ['c2','c3','c4','c5','c6','c6','c7','c8','c8','c9','c22','c23'] ,
            '3': ['c11','c11','c12','c12','c13','c14','c15','c15','c15','c15','c15','c15'] }

    census = { 'c1': 600, 'c2':90,'c3':150,'c4':120,'c5':240,'c6':300 , 'c7': 80,
            'c8':400,'c9':50, 'c11':300,'c12':400,'c13':200,'c14':220,'c15':550, 'c21':700, 'c22': 500, 'c23': 450 } 
'''



    inputdir = "Dummy_dataset_disaggregatie"

    f = f'{inputdir}/Dummy links.txt'

    areas,kol,year_header,years = create_link_dict(f)

    #stderr(years)

    census = get_census(inputdir)

    km2s = get_km(inputdir)

    
    new_res = collections.defaultdict(dict)

    i = 0
    for area in areas:
        for k in years:
            new_res[area][k] = {}
        new_res[area]['surface'] = km2s[area]
        for year in years:
            new_res[area][year]['sublevel'] = 0
            new_res[area][year]['census'] = kol[year][i]
            new_res[area][year]['status'] = 0
            new_res[area][year]['done'] = False
        i += 1

    for year in years:
        i = 0
        for j in kol[year]:
            if kol[year].count(j)==1:
                new_res[areas[i]][year]['number'] = census[j] 
                new_res[areas[i]][year]['status'] = 9
                new_res[areas[i]][year]['done'] = True
            else:
                try:
                    census[j]
                except KeyError:
                    new_res[areas[i]][year]['done'] = True
            i += 1

    lists = {}
    for year in years:
        lists[year] = sorted(list(set(kol[year])))

    tot_k = {}

    for year1 in years:
        unique_c = sorted(list(set(kol[year1])))
        #stderr(f'year1: {year1}')
        for c in unique_c:
            if c=='':
                continue
            area = areas[kol[year1].index(c)]
            if new_res[area][year1]['done']:
                continue
            all_c = [i for i, j in enumerate(kol[year1]) if j == c]
            #stderr(f'all_c: {all_c} (c: {c})')
            tot_k[year1] = census[c]
            #stderr(f'tot_k: {tot_k}')
            for year2 in years:
                skip_year = False
                if year1==year2:
                    continue
                for index in all_c:
                    #stderr(index)
                    if new_res[areas[index]][year2]['done']:
                        #oke
                        pass
                    else:
                        c2 = kol[year2][index]
                        if c2=='':
                            continue
                        all_c2 = [i for i, j in enumerate(kol[year2]) if j == c2]
                        #stderr(f'all_c2: {all_c2} (c2: {c2})')
                        for c3 in all_c2:
                            if not c3 in all_c:
                                #stderr('not oke')
                                # not oke
                                skip_year = True
                                break
                        if skip_year:
                            break
                if skip_year:
                    continue
                all_c2 = []
                for index in all_c:
                    #stderr(index)
                    all_c2.append(kol[year2][index])
                #stderr(f'all_c2: {all_c2}')
                tot_k[year2] = 0
                for c3 in sorted(list(set(all_c2))):
                    if c3!='':
                        #stderr(f'c3: {c3}')
                        try:
                            tot_k[year2] += census[c3]
                        except:
                            pass
                #stderr(f'compare years: {year1} - {year2}')
                #stderr(f'tot_k: {tot_k}')
                for i in all_c:
                    if new_res[areas[i]][year1]['done']:
                        continue
                    try:
                        new_c = census[kol[year1][i]] * census[kol[year2][i]] / tot_k[year2]
                        #stderr(f"{kol[year1][i]}, {census[kol[year1][i]]}, {new_c:>6.2f} - {kol[year2][i]}, {census[kol[year2][i]]:>3}")
                        new_res[areas[i]][year1]['number'] = new_c
                    except:
                        pass
                    if kol[year2].count(kol[year2][i])==1:
                        new_res[areas[i]][year1]['status'] = 8
                        new_res[areas[i]][year1]['done'] = True
                        new_res[areas[i]][year1]['sublevel'] += 1
                        new_res[areas[i]][year2]['sublevel'] += 1
                    else:
                        new_res[areas[i]][year1]['status'] = 7
                        new_res[areas[i]][year1]['sublevel'] = new_res[areas[i]][year1]['sublevel']
                        if not new_res[areas[i]][year2]['done']:
                            new_res[areas[i]][year2]['status'] = 7
                            new_res[areas[i]][year2]['number'] = census[kol[year2][i]]
                            new_res[areas[i]][year2]['sublevel'] = new_res[areas[i]][year2]['sublevel']



    stderr('calculate based on surfaces')
    for year in years:
        for area in new_res:
            debug = False
            if not new_res[area][year]['done']:
                c = new_res[area][year]['census']
#                if year=='1374' and c=='census_BR1374a_628':
#                    debug = True
                areas2 = find_all(new_res,year,c,debug=debug)
                if debug:
                    stderr(f'areas2: {areas2}')
                tot_surface = 0.0
                for a in areas2:
                    if not new_res[a][year]['done']:
                        tot_surface += new_res[a]['surface']
                if debug:
                    stderr(f'tot_surface: {tot_surface}')
                    stderr(f'area: {area}')
                    stderr(f'year: {year}')
                    stderr(f'new_res: {new_res[area][year]}')
                for a in areas2:
                    if not 'number' in new_res[a][year]:
                        new_res[a][year]['number'] = \
                            census[new_res[a][year]['census']]
                    new_res[a][year]['number'] = \
                        new_res[a][year]['number'] * new_res[a]['surface'] / tot_surface
                    new_res[a][year]['status'] = 6
                    new_res[a][year]['done'] = True
                if debug:
                    stderr(f'new_res: {new_res[area][year]}')



    new_rows = []
    for k,v in new_res.items():
        new_row = [k]
        new_row.append(v['surface'])
        for year in years:
            try:
                new_row.append(v[year]['number'])
                new_row.append(v[year]['status'])
                new_row.append(v[year]['census'])
                new_row.append(census[v[year]['census']])
            except:
                new_row.append('');
                new_row.append('');
                new_row.append('');
                new_row.append('');
        new_rows.append(new_row)



    columns = ['Area','km2']
    for year in years:
        columns.append(f'{year_header[year]}')
        columns.append(f'stat')
        columns.append(f'census')
        columns.append(f'orig')
    new_df = pd.DataFrame(new_rows, columns=columns)
    new_df.to_excel('test_res_10a.xlsx')

    end_prog()

