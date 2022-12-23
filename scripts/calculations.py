# -*- coding: utf-8 -*-
import re

class Calculations:

    def __init__(self):
        pass

    def find_year(self,census):
        return int(re.search(r'\d{4}',census).group(0))

    def calc_dist(self,years):
        result = {}
        for year in years:
            result[year] = []
            y1 = self.find_year(year)
            for y2 in years:
                if y2!=year:
                    y3 = self.find_year(y2)
                    result[year].append((abs(y1-y3),y2))
                result[year] = sorted(result[year])
        res = {}
        for (k,v) in iter(result.items()):
            res[k] = []
            for y in v:
                res[k].append(y[1])
        return res

