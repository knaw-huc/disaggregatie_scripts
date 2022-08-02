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
    stderr(all_files)
    census_list = {}
    all_data = {}

    for f in all_files:
        basename = os.path.basename(f).replace('census_','').replace('.txt','')
        year = re.search(r'(\d\d\d\d)',basename).group(1)
        stderr(basename)
#        br1526a = pd.read_csv(f, sep='\t', usecols=['UUID', 'YEAR', 'PRIMARY_UNIT'],index_col=0).to_dict()
        try:
            df = pd.read_csv(f, sep='\t', usecols=['UUID', 'YEAR', 'PRIMARY_UNIT'])
            if True:
                all_data[basename] = df
                census_list[year] = basename
#            stderr(f)
#            stderr(df.shape)
#            stderr(df.info(verbose=False))
#            df.to_excel(basename)
        except ValueError as vErr:
            basename = os.path.basename(f).replace('txt','xlsx')
            stderr(basename)
            df = pd.read_csv(f, sep='\t')
            df.to_excel(basename)
            stderr(vErr)
            stderr(f)
    stderr(census_list)
    stderr('all_data.keys:')
    stderr(all_data.keys())
    stderr(all_data['BR1526a'].keys())
#    exit(1)

#    stderr(df.to_string())

#    df = pd.read_csv('Dummy_dataset_disaggregatie/Dummy links.txt', sep='\t')
#    stderr(df.info(verbose=True))
#    df.to_excel("output.xlsx") 



# lees 'Dummy links.txt'
# per row (SHORT_ID) neem elke column (eerst alleen BR1526a)
# neem gegevens uit het betreffende bestand (PRIMARY_UNIT)
# maak row: Plaats, Code, Jaartal(len)

    f = f'{inputdir}/Dummy links.txt'
    links = pd.read_csv(f, sep='\t')
    links_cols = links.columns
    stderr(links_cols)
    year_cols = {}
    for l in links_cols:
        try:
            res = re.search(r'(\d\d\d\d)',l).group(1)
            year_cols[res] = l
        except:
            pass
    stderr(year_cols)
    
#    for row in links.itertuples():
#        stderr(row.__class__)
#        stderr(getattr(row,'BR1526a'))

#    f = f'{inputdir}/Census_BR1526a.txt'
#    br1526a = pd.read_csv(f, sep='\t', usecols=['UUID', 'YEAR', 'PRIMARY_UNIT'],index_col=0).to_dict()
#    stderr(br1526a['PRIMARY_UNIT'])
    
#    with open(f, newline='') as csvfile:
#        reader = csv.DictReader(csvfile,delimiter='\t')
#        for row in reader:
#            stderr(f"{row['UUID']}, {row['PRIMARY_UNIT']}")
#    exit(1)

    data = []
    teller = 0
    years = sorted(census_list.keys())
    stderr(years)
    for row in links.itertuples():
        short_id = getattr(row,'SHORT_ID')
#        stderr(f'{short_id} - {lookfor}')a
        this_row = {}
        this_row['Code'] = short_id
        for year in years:
            col = year_cols[year]
#            res = 
            lookfor = getattr(row,col)
            stderr(f'lookfor: {lookfor}')
            try:
                stderr(census_list[year])
                stderr(all_data[census_list[year]].__class__)
                df = all_data[census_list[year]]
                res = df.loc[df['UUID'] == lookfor] #["PRIMARY_UNIT"][1]
                stderr(f'res:\n{res}')
                res = res.iloc[0]['PRIMARY_UNIT']
#                stderr(f'1: {res["PRIMARY_UNIT"]}')
#                stderr(f'2: {res["PRIMARY_UNIT"][1]}')
#                stderr(f'3: {res["PRIMARY_UNIT"][1].__class__}')
  #              stderr(all_data[census_list[year]]['UUID'])
   #             res = all_data[census_list[year]]['UUID'][lookfor]
                # res = br1526a['PRIMARY_UNIT'][lookfor]
                stderr(f'res: {res}')
                this_row[year] = res
            except Exception as err:
                stderr(f'err: {err}')
                pass
        stderr(this_row)
        data.append(this_row)
        teller += 1
        if teller>100:
            break

    new_df = pd.DataFrame(data, columns=['Code'] + years)
    new_df.to_excel('text_res.xlsx')

    end_prog(0)
    
