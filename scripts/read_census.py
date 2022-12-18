# -*- coding: utf-8 -*-
import csv

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

