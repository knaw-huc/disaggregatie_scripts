# -*- coding: utf-8 -*-
#from distances import calc_dist,find_year
from area import Area
import argparse
import calculations as calc
from census import Census
from censuscollection import CensusCollection
from datetime import datetime
import glob
import json
import readandwrite as rw
import pprint as pp
import sys


# calc.search_double_values(all_census,areas)
def search_multiple(all_census,areas,number,debug=False):
    if debug:
        print(f'number: {number}')
        stderr(f'\nnumber: {number}')
    teller = 0
    count_poss = 0
    count_ready = 0
    count_compl = 0
    cl = all_census.get_census_coll()
    # search all census
    number_to_investigate = number
    for census_code in cl:
        census = cl[census_code]
        counted = census.get_counted()
        # take those who cover two areas
        if census.number_of_areas() == number_to_investigate:
            if debug:
                stderr(census_code)
            # follow the search order for the years
            try:
                search_ord  = search_order[census.get_census_id()]
            except KeyError:
                stderr(census.get_census_id())
                stderr(census)
                stderr('(A) Ends with KeyError')
                exit(1)
            for census_id in search_ord:
                if debug:
                    stderr(f'census_id: {census_id}')
                area_codes = census.get_areas()
                # take each area in a census of another year
                count_readys = 0
                ready_c_s = []
                for ac in area_codes:
                    area = areas.get_area(ac)
                    if area.ready(census_code):
                        count_ready =+ 1
                        continue
                    count_poss += 1
                    acl = area.get_census_list()
                    # in an area look for a census of the year we are currently looking at
                    for c in acl:
                        compare_census = all_census.get_census(c)
                        try:
                            if compare_census.get_census_id() == census_id:
                            # now we want to know:
                            # is this a 'ready census'?
                            # if yes than perhaps we can calculate the population for the census
                            # we are investigating
                            # but only if this is valid for all areas
                                if area.ready(c):
                                    count_readys += 1
                                    ready_c_s.append(c)
                        except Exception as e:
                            stderr(f'census_id: {census_id}')
                            stderr(f'acl: {acl}')
                            stderr(f'c: {c} ({compare_census.__class__})')
                            stderr(f'(B) Ends with: {e}')
                            exit(1)
                        # stderr(f'c: {c} no')
                    # if count_readys equals number_to_investigate we can calculate the
                    # populations for the areas of this census
                if count_readys == number_to_investigate:
                    if debug:
                        stderr('start calculating')
                    calc.calc_population_spread(all_census,areas,ready_c_s,census,debug=debug)
                    count_compl += 1
            teller += 1
#        if teller > 1000:
#            break;
    if debug:
        print(f'count_poss: {count_poss}')
        print(f'count_ready: {count_ready}')
        print(f'count_compl: {count_compl}')
        print('')




def end_prog(code=0):
    if code!=0:
        code_str = f' (met code {code})'
    else:
        code_str = ''
    stderr(datetime.today().strftime(f"einde: %H:%M:%S{code_str}"))
    sys.exit(code)


def stderr(text,nl='\n'):
    sys.stderr.write(f"{text}{nl}")


def arguments(ap):
    ap.add_argument('-c', '--config',
                    help="config",
                    default = "config.json")
    ap.add_argument('-i', '--inputdir',
                    help="inputdir")
    ap.add_argument('-o', '--outputfile',
                    help="outputfile")
    ap.add_argument("-d", "--debug",
                    help="debug - default: false",
                    action="store_true")
    args = vars(ap.parse_args())
    return args


if __name__ == '__main__':
    stderr(datetime.today().strftime("start: %H:%M:%S"))

    ap = argparse.ArgumentParser(description='Disaggregatie census files')
    args = arguments(ap)
    config_file = args['config']
    with open(config_file) as f:
        config = json.load(f)
        inputdir = config.get('inputdir','')
        outputfile = config.get('outputfile','')
        surface_file = config.get('surface_file','')
        links_file = config.get('links_file','')
        census_files = config.get('census_files','')
    if inputdir=='':
        try:
            inputdir = args["inputdir"]
        except:
            inputdir = ''
            pass
    if outputfile=='':
        try:
            outputfile = args["outputfile"]
        except:
            pass
    debug = args["debug"]

    stderr(f'''
reading from directory: {inputdir}
census files matching:  {census_files}
surfaces file:          {surface_file}
links file:             {links_file}
writing to:             {outputfile}
debug is {debug}
''')
    if '' or None in [inputdir, outputfile, surface_file, links_file, census_files]:
        stderr('Please fill in all the necessary values in the config file')
        end_prog(1)

    # read census files: census code and population count
    all_census = CensusCollection()
    all_files = glob.glob(f"{inputdir}/{census_files}")
    for f in all_files:
        rw.read_census(f,all_census,debug=debug)

    # read file linking area with census
    f = f'{inputdir}/{links_file}'
    areas,all_census,year_header,years = rw.create_link_dict(f,all_census,debug=debug)
    
    census_id_list = list(map(lambda x: f'census_{x}' ,year_header.values()))
    search_order = calc.calc_dist(census_id_list)

    if debug:
        stderr(f'num of areas: {areas.get_number_of_areas()}')
        stderr(f'num of census: {all_census.get_number_of_census()}')
        stderr(year_header)
        stderr(years)
    if isinstance(all_census,CensusCollection):
        if debug:
            stderr('OK')
    else:
        if debug:
            stderr('not OK')
            stderr(all_census.__name__)

    f = f'{inputdir}/{surface_file}'
    areas = rw.read_surfaces(f,areas)
    if debug:
        stderr(f'num of areas: {areas.get_number_of_areas()}')
        stderr(f' number of census: {all_census.get_number_of_census()}')

    calc.fill_single_values(all_census,areas)

    max_areas = all_census.get_max_areas()
    if debug:
        stderr(f'max_areas: {max_areas}')
    for number in range(2,max_areas+1):
        search_multiple(all_census,areas,number)

    largest_perc = 0.0
    best_census_id = ''
    for census_id in census_id_list:
        res = all_census.get_number_ready(census_id,areas)
        if res > largest_perc:
            largest_perc = res
            best_census_id = census_id
        if debug:
            stderr(f'{census_id}: {res}')
    if debug:
        stderr(f'best: {best_census_id}: {largest_perc}\n')

    calc.calculate_using_surface(best_census_id,all_census,areas)

    max_areas = all_census.get_max_areas()
    if debug:
        stderr(f'second round:')
        stderr(f'max_areas: {max_areas}')
    for number in range(2,max_areas+1):
        search_multiple(all_census,areas,number)

    for census_id in census_id_list:
        calc.calculate_using_surface(census_id,all_census,areas)


    compact = False
    result = calc.build_matrix(areas,years,all_census,compact)
    headers = ['area','surface']

    for year in years:
        headers.append(year_header[year])
        if not compact:
            headers.append(year)
            headers.append('orig')

    if debug:
        stderr(f'headers: {len(headers)}')
        stderr(f'result: {len(result[0])}')
    rw.make_xlsx(headers,result,uitvoer=outputfile)


    end_prog()


