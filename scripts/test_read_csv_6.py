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
        stderr(headers)
#        del(headers[0])
#        stderr(headers)
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
    print('id_census:') 
    pp.pprint(id_census)
    print('\n\ncensus_id:') 
    pp.pprint(census_id)
    print('\n')
#    for k,v in census_id.items():
#        if len(v)==1:
#            print(f'{k}: {v}')
    return

def check_row(row):
    num_codes = 0
    for year in years:
        cell = row[year]
        try:
            if cell.startswith('census'):
                num_codes += 1
        except:
            pass
    return num_codes > 1


def check_equal(row,data,col_dict,check_num):
    codes = []
    for year in years:
        cell = row[year]
        try:
            if cell.startswith('census'):
                codes.append(cell)
        except:
            pass
    count = 0
    saved_rows = []
    for row in data:
        found_one = False
        this_res = True
        for year in years:
            cell = row[year]
            try:
                if cell.startswith('census'):
                    if cell in codes:
                        found_one = True
                        check_num = col_dict[cell]
                        saved_rows.append(row)
                    else:
                        this_res = False
            except:
                pass
        if found_one and this_res:
            count += 1
    if check_num != count:
        return []

    for year in years:
        this_cell = ''
        this_cell_type = None
        for row in saved_rows:
            cell = row[year]
            if this_cell_type:
                if type(cell) != this_cell_type:
                    return []
            else:
                this_cell_type = type(cell)
            try:
                if cell.startswith('census'):
                    if this_cell=='':
                        this_cell = cell
                    else:
                        if this_cell != cell:
                            return []
            except:
                pass
    return saved_rows

def data_aanpassen(row,saved_rows,data,col_dict,check_num):
    to_convert = []
    converted = []
    for key in saved_rows[0].keys():
        cell = saved_rows[0][key]
        try:
            if cell.startswith('census'):
                to_convert.append(key)
        except:
            if not math.isnan(cell):
                converted.append(key)

    if len(converted)==0:
        return

    totals = {}
    for year in converted:
        total = 0
        for row in saved_rows:
            total += row[year]
        totals[year] = total

    for year in to_convert:
        for row in saved_rows:
            cell = row[year]
            try:
                if cell.startswith('census'):
                    #df = all_data[census_list[year]]
                    #res = df.loc[df['UUID'] == cell]
                    res = calculate(get_data(year,cell), row[converted[0]],totals[converted[0]])
                    row[year] = res
            except Exception as err:
                stderr(f'err: {err}')
                pass

def get_data(year,cell):
    df = all_data[census_list[year]]
    res = df.loc[df['UUID'] == cell]
    try:
#        stderr(f'census_list[{year}]: {census_list[year]}')
#        stderr(f'res: {res}')
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
    #colObj[i],diff_col_obj[i],count_diff_col):
    return (a * b) / c

def make_selection(data,census):
    new_data = []
    for row in data:
        if row['1374']==census:
            new_data.append(row)
    return new_data

def recalculate(data):
    best_year = 0
    best_count = 0
    for year in years:
        count = 0
        for row in data:
            if type(row[year]) == np.int64:
                count += 1
        if count>best_count:
            best_count = count
            best_year = year
        #stderr(f'{year}: {count}')
    #stderr(f'best_year: {best_year}')
    best_year_col = 0
    add_once = 0
    calc_surf = []
    added_surf = 0.0
    for row in data:
        if type(row[best_year]) != np.int64:
            row[best_year] = get_data(best_year,row[best_year])
            add_once = row[best_year]
            calc_surf.append(row['Code'])
            added_surf += surfaces[row['Code']]
        else:
            best_year_col += row[best_year]
    best_year_col += add_once
    stderr(f'total: {best_year_col}')
    stderr(f'calc cols: {calc_surf}')
    stderr(f'added surf: {added_surf}')
    for year in years:
        if year==best_year:
            continue
        add_once = 0
        total = 0
        for row in data:
            if type(row[year]) != np.int64:
                try:
                    row[year] = calculate(get_data(year,row[year]),row[best_year],best_year_col)
                except:
                    pass
    # after this, information is lost on which rows need to be calculated on basis of their surface
    # so, the calculation has to be done here
    for year in years:
        for row in data:
            if row['Code'] in calc_surf:
                try:
                    row[year] = calculate(float(row[year]), surfaces[row['Code']], added_surf)
                except Exception as err:
                    stderr(f'error? {err}') 
                    pass

def split_on_area(census,areas):
    stderr(f'census: {census} - areas: {areas}')
    year = get_year(census)
    stderr(f'year: {year}')
    tot_area = 0.0
    census_value = get_census_value(census)
    for a in areas:
        tot_area += surfaces[a]
    stderr(f'tot area: {tot_area}')
    for i in range(len(areas)):
        surf = surfaces[areas[i]]
        stderr(f'surf: {surf}')
        new_val = calculate(census_value, surf, tot_area)
        stderr(f'new_val: {new_val}')
        add_value(areas[i],year,new_val)

def split_population(census,cc,areas):
    stderr(f'census: {census} - cc: {cc} - areas: {areas}')
    year = get_year(census)
    stderr(f'year: {year}')
    val = get_census_value(census)
    stderr(f'val: {val}')
    ref_total = 0
    for c in cc:
        ref_total += get_census_value(c)
    stderr(f'ref_total: {ref_total}')
    for i in range(len(areas)):
        new_val = calculate(val,get_census_value(cc[i]),ref_total)
        stderr(f'new_val: {new_val}')
        add_value(areas[i],year,new_val)

def remainder():
    pass


def add_value(area,year,val):
    new_res[area][year] = val

def get_year(k):
    year = re.search(r'(\d\d\d\d)',k).group(1)
    return year

def get_value(year,cell):
    val = get_data(year,cell)
    return val

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
#            if v[0] not in new_res:
#                new_res[v[0]] = {}
            stderr(f'k: {k}: {v}')
            for c in v:
                for c2 in id_census[c]:
                    stderr(f'{c}: {c2}')
                    if c2!=k:
                        if len(census_id[c2])==1:
                            count +=1
                            cc.append(c2)
                        elif len(census_id[c2])==area_num:
                            area_split +=1
                    else:
                        area_split += 1
            if count==area_num:
                stderr('split on population')
                split_population(k,cc,v)
            elif area_split==area_num:
                stderr('split on area')
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
#            if v[0] not in new_res:
#                new_res[v[0]] = {}
            #stderr(f'k: {k}: {v}')
            val = get_census_value(k)
            add_value(v[0],get_year(k),val)

    lengtes = []
    for v in census_id.values():
        if not len(v) in lengtes:
            lengtes.append(len(v))
    lengtes.sort()
    stderr(lengtes)
    res = max(len(elem) for elem in census_id.values())
    stderr(f'res: {res}')
    for i in range(2,res+1):
        stderr(i,' ')
    stderr(' ')

#   two areas
    area_num = 2
    for area_num in range(2,res+1):
        recalc(area_num)

    # calculate remainder on basis of surface
    remainder()

    print('\n')
    pp.pprint(new_res)

    '''
    for k,v in census_id.items():
        if len(v)==area_num:
            count = 0
            area_split = 0
            cc = []
#            if v[0] not in new_res:
#                new_res[v[0]] = {}
            stderr(f'k: {k}: {v}')
            for c in v:
                for c2 in id_census[c]:
                    stderr(f'{c}: {c2}')
                    if c2!=k:
                        if len(census_id[c2])==1:
                            count +=1
                            cc.append(c2)
                        elif len(census_id[c2])==area_num:
                            area_split +=1
            if count==area_num:
                stderr('split on population')
                split_population(k,cc,v)
            elif area_split==area_num:
                stderr('split on area')
                split_on_area(k,v)
            # zoek naar andere censussen die voor deze area wel uitgesplitst zijn
            # gevonden: uitsplitsen volgens verhoudingen,
            # niet gevonden: uitsplitsen volgens oppervlakte.

#            year = get_year(k)
#            val = get_value(year,k)
#            new_res[v[0]][year] = val
'''
    print('\n')
    pp.pprint(new_res)

    #end_prog(1)

    '''

#   find census met meerdere areas en kijk dan of die areas allemaal naar de zelfde censussen verwijzen

    for area,values in id_census.items():
        skip = False
#        if not area.startswith('BR0050'):
#            continue
        #stderr(f'area: {area}')
        save = []
        save_uniq = []
        for census in values:
#            stderr(census)
            if len(census_id[census])>1:
                if len(save)==0:
                    save = census_id[census]
                else:
                    if save!=census_id[census]:
                        skip = True
            else:
                if len(save)>0:
                    if census_id[census][0] not in save:
                        skip = True
                    else:
                        y = re.search(r'(\d\d\d\d)',census).group(1)
                        try:
                            exists = new_res[area][y]
                            save_uniq.append(census)
                        except:
                            pass
            #for v in census_id[census]:
            #    stderr(f'{v}')
        if len(save_uniq)==0 or len(save_uniq)==len(new_res[area]):
            skip = True
        if not skip:
            stderr(f'compute: {area}')
            stderr(f'save: {save}')
            stderr(f'save_uniq: {save_uniq}')
            part = 'census_' + save_uniq[0].split('_')[1]
            #stderr(f'part: {part}')
            c_list = []
            for area in save:
                for cens in id_census[area]:
                    if re.search(part, cens):
                        c_list.append(cens)
                        #stderr(id_census[area])
            uniq_year = re.search(r'(\d\d\d\d)',save_uniq[0]).group(1)
            ref_total = 0.0
            refs = {}
            try:
                for area in save:
                    refs[area] = float(new_res[area][uniq_year])
                    ref_total += float(new_res[area][uniq_year])
            except:
                continue
            #stderr(refs)
            #stderr(ref_total)
            for area in save:
                #stderr(f'area: {area}')
                #stderr(f'years: {new_res[area]}')
                #for y in new_res[area]:
                    #stderr(f'y: {y} ({y.__class__}) - {new_res[area][y]}')
                for cens in id_census[area]:
                    #stderr(f'cens: {cens}')
                    y = re.search(r'(\d\d\d\d)',cens).group(1)
                    #stderr(f'year: {y} ({y.__class__})')
                    try:
                        #stderr(f'try: {new_res[area][y]}')
                        exists = new_res[area][y]
                        #stderr(f'exist: {exists}')
                    except:
                        stderr('new one')
                        stderr(f'area: {area}')
                        stderr(f'cens: {cens}')
                        val = get_value(y,cens)
                        #stderr(f'val: {val}')
                        calc_val = calculate(val,refs[area],ref_total)
                        #stderr(f'calc_val: {calc_val}')
                        new_res[area][y] = calc_val



    end_prog(1)


    for key,values in census_id.items():
        debug = False
        skip = False
        if len(values)>1:
            save = []
            single_found = False
            for area in values:
                if area.startswith('BR0050'):
                    debug = True
                if debug:
                    stderr(id_census[area])
                if len(save)==0:
                    save = id_census[area]
                else:
                    if save!=id_census[area]:
                        if debug:
                            stderr('diff')
                        for census in (set(save) - set(id_census[area])):
                            if not len(census_id[census])==1:
                                skip = True
                            else:
                                single_found = True
                    else:
                        if debug:
                            stderr('no diff')
        else:
            continue
        if not skip and single_found:
            #pass
            if not debug:
                continue
            stderr('found one?')
            stderr(f'{key}: {values}')


#   try the find those areas that belong to one census and are not split in an other census
#   i.e. area_code A contains census X,Y,Z and census X,Y,Z only contain area_code A
    for key,values in census_id.items():
        if len(values)==1:
            continue
        skip = False
        for area in values:
            if len(id_census[area])>1:
                skip = True
                break
        if not skip:
            stderr(f'deze: {key}: {values} ?')
        

'''


    build_table = []
    for key in id_census.keys():
    #for key in new_res.keys():
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

    end_prog(1)


    year_cols = {}
    for l in links_cols:
        try:
            res = re.search(r'(\d\d\d\d)',l).group(1)
            year_cols[res] = l
        except:
            pass

    unique_codes = []
    for year in years:
        col = year_cols[year]
        col_data = links.loc[:,col]
        col_dict = dict(Counter(col_data))
        for k in col_dict.keys():
            if col_dict[k] == 1:
                unique_codes.append(k)

    data = []
    teller = 0
    for row in links.itertuples():
        short_id = getattr(row,'SHORT_ID')
        this_row = {}
        this_row['Code'] = short_id
        for year in years:
            col = year_cols[year]
            lookfor = getattr(row,col)
            if not lookfor in unique_codes:
                this_row[year] = lookfor
                continue
            try:
                df = all_data[census_list[year]]
                res = df.loc[df['UUID'] == lookfor]
                res = res.iloc[0]['PRIMARY_UNIT']
                this_row[year] = res
            except Exception as err:
#                stderr(f'err: {err}')
                pass
        data.append(this_row)
        teller += 1

    checked = []
    for row in data:
        num = 0
        oke = True
        cell = row['Code']
        if cell in checked:
            oke = False
            break
        checked.append(cell)
        for year in years:
            cell = row[year]
            try:
                if cell.startswith('census'):
                    if oke and col_dict[cell] > 1 and num > 0:
                        if num != col_dict[cell]:
                            oke = False
                            break
                    else:
                        num = col_dict[cell]
            except:
                pass
        if num==0:
            continue
        if oke:
            oke = check_row(row)
        if oke:
            try:
                saved_rows = check_equal(row,data,col_dict,num)
                if len(saved_rows)>0:
                    oke = True
                else:
                    oke = False
            except Exception as err:
                stderr(err)
                stderr(type(err))
                stderr(err.args)
                stderr(row)
                exit(1)
        if oke:
            data_aanpassen(row,saved_rows,data,col_dict,num)

#    new_df = pd.DataFrame(data, columns=['Code'] + years)

#    selection = make_selection(data,'census_BR1374a_147')
    selection = data
    recalculate(selection)
    new_df = pd.DataFrame(selection, columns=['Code'] + years)

    new_df.to_excel('test_res_6.xlsx')

    end_prog(0)

