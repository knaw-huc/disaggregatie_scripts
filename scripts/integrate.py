# -*- coding: utf-8 -*-
#from distances import calc_dist,find_year
from area import Area
import calculations as calc
from census import Census
from censuscollection import CensusCollection
from datetime import datetime
import glob
import readandwrite as rw
import pprint as pp
import sys


# calc.search_double_values(all_census,areas)
def search_multiple(all_census,areas,number):
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
            print(census_code)
            # follow the search order for the years
            try:
                search_ord  = search_order[census.get_census_id()]
            except KeyError:
                stderr(census.get_census_id())
                stderr(census)
                stderr('(A) Ends with KeyError')
                exit(1)
            for census_id in search_ord:
                print(f'census_id: {census_id}')
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
                    print('start calculating')
#                    stderr('start calculating:')
#                    stderr(f'{ready_c_s} can be used to calculate')
#                    stderr(f'areas {census.get_areas()} in {census_code}')
                    calc.calc_population_spread(all_census,areas,ready_c_s,census)
                    count_compl += 1
                    #stderr(f'census_id: {census_id}')
                    #stderr(f'ac: {ac}')
                    #stderr(f'{census}')
                    #stderr(f'{census.get_areas()}')
#                else:
#                    if count_readys>0:
#                        stderr(f'{count_readys} = not {number_to_investigate}')
            teller += 1
#        if teller > 1000:
#            break;
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


if __name__ == '__main__':
    stderr(datetime.today().strftime("start: %H:%M:%S"))

    inputdir = "Dummy_dataset_disaggregatie"

    # read census files: census code and population count
    all_census = CensusCollection()
    all_files = glob.glob(f"{inputdir}/census_*.txt")
    for f in all_files:
        rw.read_census(f,all_census)

    # read file linking area with census
    f = f'{inputdir}/Dummy links.txt'
    areas,all_census,year_header,years = rw.create_link_dict(f,all_census)

#    br1374a = all_census.get_census(census_BR1374a)
    with open('inspect_census_BR1374a.txt','w') as uitvoer:
        for census_code in all_census:
            census = all_census.get_census(census_code)
            if census.get_census_id() == 'census_BR1374a':
                uitvoer.write(f'{census}\n')
    
    census_id_list = list(map(lambda x: f'census_{x}' ,year_header.values()))
    search_order = calc.calc_dist(census_id_list)

    stderr(f'num of areas: {areas.get_number_of_areas()}')
    stderr(f'num of census: {all_census.get_number_of_census()}')
    stderr(year_header)
    stderr(years)
    if isinstance(all_census,CensusCollection):
        stderr('OK')
    else:
        stderr('not OK')
        stderr(all_census.__name__)

    f = f'{inputdir}/Dummy km2.txt'
    areas = rw.read_surfaces(f,areas)
    stderr(f'num of areas: {areas.get_number_of_areas()}')
    #stderr(f'class of areas: {areas.__class__}')

    #for key,value in areas.items():
        #stderr(key)
        #stderr(value)
        #stderr(f"{value.get_census_list()}"[0:500])
        #break

    stderr(f' number of census: {all_census.get_number_of_census()}')
    stderr(f"{areas.get_area('BR0010B6')}")
    stderr(f"{len(areas.get_area('BR0010B6').get_census_list())}")
    stderr(f"{areas.get_area('BR0010B6').get_census_list()}")
    stderr(f"{areas.get_area('BR0010B5')}")
    stderr(f"{len(areas.get_area('BR0010B5').get_census_list())}")
    stderr(f"{areas.get_area('BR0010B5').get_census_list()}")
    census = all_census.get_census('census_BR1374a_628')
    stderr(census)

    calc.fill_single_values(all_census,areas)

    area = areas.get_area('ME0010A')
    stderr(area)
    stderr(area.ready('census_ME1544a_1'))
    stderr(area.get_census_population('census_ME1544a_1'))

    max_areas = all_census.get_max_areas()
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
        stderr(f'{census_id}: {res}')
    stderr(f'best: {best_census_id}: {largest_perc}\n')

    calc.calculate_using_surface(best_census_id,all_census,areas)

    max_areas = all_census.get_max_areas()
    stderr(f'second round:')
    stderr(f'max_areas: {max_areas}')
    for number in range(2,max_areas+1):
        search_multiple(all_census,areas,number)


    compact = False
    result = calc.build_matrix(areas,years,all_census,compact)
    headers = ['area','surface']

    for year in years:
        headers.append(year_header[year])
        if not compact:
            headers.append(year)
            headers.append('orig')

    stderr(f'headers: {len(headers)}')
    stderr(f'result: {len(result[0])}')
    rw.make_xlsx(headers,result,uitvoer='new_try_02.xlsx')


    end_prog()


