# -*- coding: utf-8 -*-
import csv
#import json
#import psycopg2
#from config import config
from datetime import datetime
import glob
import os.path
import re
import sys
import pandas as pd



def end_prog(code=0):
    stderr(datetime.today().strftime("einde: %H:%M:%S"))
    sys.exit(code)

def stderr(text):
    sys.stderr.write("{}\n".format(text))

if __name__ == '__main__':
    stderr(datetime.today().strftime("start: %H:%M:%S"))

    inputdir = "Dummy_dataset_disaggregatie"

    print(pd.options.display.max_rows) 

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

    data = []
    teller = 0
    years = sorted(census_list.keys())
    for row in links.itertuples():
        short_id = getattr(row,'SHORT_ID')
        this_row = {}
        this_row['Code'] = short_id
        for year in years:
            col = year_cols[year]
            lookfor = getattr(row,col)
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

    new_df = pd.DataFrame(data, columns=['Code'] + years)


    for col in new_df[years]:
        colObj = new_df[col]
        stderr(colObj.__class__)
        rem_last = False
        for i in range(len(colObj)):
            if i>0:
                if colObj[i]==colObj[i-1]:
                    colObj[i-1] = None
                    rem_last = True
                else:
                    if rem_last:
                        colObj[i-1] = None
                        rem_last = False
        if rem_last:
            # also remove last in series (if equal to previous)
            colObj[len(colObj)-1] = None
    new_df.to_excel('test_res_2.xlsx')

    end_prog(0)
    
