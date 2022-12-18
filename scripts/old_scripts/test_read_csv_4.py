# -*- coding: utf-8 -*-
import csv
#import json
#import psycopg2
#from config import config
from collections import Counter
from datetime import datetime
import glob
import math
import numpy as np
import os.path
import re
import sys
import pandas as pd


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
                    df = all_data[census_list[year]]
                    res = df.loc[df['UUID'] == cell]
                    res = calculate(res.iloc[0]['PRIMARY_UNIT'],row[converted[0]],totals[converted[0]])
                    row[year] = res
            except Exception as err:
                stderr(f'err: {err}')
                pass


def calculate(a,b,c):
    #colObj[i],diff_col_obj[i],count_diff_col):
    return (a * b) / c

def end_prog(code=0):
    if code!=0:
        code_str = f' (met code {code})'
    else:
        code_str = ''
    stderr(datetime.today().strftime(f"einde: %H:%M:%S{code_str}"))
    sys.exit(code)

def stderr(text):
    sys.stderr.write("{}\n".format(text))

if __name__ == '__main__':
    stderr(datetime.today().strftime("start: %H:%M:%S"))

    inputdir = "Dummy_dataset_disaggregatie"

    all_files = glob.glob(f"{inputdir}/census_*.txt")
    census_list = {}
    all_data = {}


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

    f = f'{inputdir}/Dummy links.txt'
    links = pd.read_csv(f, sep='\t')
    links_cols = links.columns

    year_cols = {}
    for l in links_cols:
        try:
            res = re.search(r'(\d\d\d\d)',l).group(1)
            year_cols[res] = l
        except:
            pass

    years = sorted(census_list.keys())
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

    new_df = pd.DataFrame(data, columns=['Code'] + years)

    new_df.to_excel('test_res_5.xlsx')

    end_prog(0)

