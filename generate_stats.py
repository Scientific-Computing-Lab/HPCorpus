from csv import DictReader
from datetime import datetime
import json


def unite_paradigms():
    '''
    Join the different JSON files by repo name
    '''
    repos = {}

    for lang in ['Fortran', 'c', 'cpp']:
        with open(f'analyzed_data/{lang}_paradigms.json', 'r') as f:
            paradigms = json.loads(f.read())

            for repo, pars in paradigms.items():
                if repo not in repos:
                    repos[repo] = {'CUDA': False, 'OpenCL': False, 'OpenACC': False, 'SYCL': False, 
                                          'TBB': False, 'Cilk': False, 'OpenMP': False, 'MPI': False}

                for par, val in pars.items():
                    repos[repo][par] |= val

    with open('analyzed_data/total_paradigms.json', 'w') as f:
        f.write(json.dumps(repos))

    
def get_repo_metadata(metadata_filepath):
    '''
    Load metadata - fork, creation and last update time of each repo
    '''
    metadata = {}
    prefix = 'https://github.com/'
    suffix = '.git'

    with open(metadata_filepath, 'r') as f:
        dict_reader = DictReader(f)

        for line in list(dict_reader):
            creation_time = datetime.strptime(line['creation_time'], '%Y-%m-%dT%H:%M:%SZ')
            update_time = datetime.strptime(line['update_time'], '%Y-%m-%dT%H:%M:%SZ')
            fork = True if line['fork'] == 'True' else False

            metadata[line['URL'][len(prefix): -len(suffix)]] = {'creation_time': creation_time, 'update_time': update_time, 'fork': fork}

    return metadata


# def debug(metadata_filepath):

#     metadata = get_repo_metadata(metadata_filepath)
#     with open('analyzed_data/total_paradigms.json', 'r') as f:
#         paradigm_per_repo = json.loads(f.read())

#         for repo in metadata:
#             if repo not in paradigm_per_repo:
#                 print(repo)
    
    

def get_paradigms_over_time(paradigm_list, metadata_filepath, avoid_fork=True, key='update_time'):
    '''
    Get the number of repositories that used different parallelization APIs per month.
    '''
    repos_over_time = {}
    total = 0
    metadata = get_repo_metadata(metadata_filepath)

    with open('analyzed_data/total_paradigms.json', 'r') as f:
        paradigm_per_repo = json.loads(f.read())

        for repo, paradigms in paradigm_per_repo.items():
            if repo in metadata and all([val for paradigm ,val in paradigms.items() if paradigm in paradigm_list]):
                total += 1

                if avoid_fork and metadata[repo]['fork']:
                    continue

                dt_object = metadata[repo][key]

                year = dt_object.year
                month = dt_object.month

                if year not in repos_over_time:
                    repos_over_time[year] = {}

                if month not in repos_over_time[year]:
                    repos_over_time[year][month] = 0

                repos_over_time[year][month] += 1

    return repos_over_time


def get_total_repos_over_time(metadata_filepath):
    '''
    Figure 2

    Get the total usage of HPCorpus repositories
    '''
    paradigm_per_year = {}
    paradigm_over_time = get_paradigms_over_time([], metadata_filepath, avoid_fork=False, key='creation_time')

    for year in paradigm_over_time:
        paradigm_per_year[year] = sum(paradigm_over_time[year].values())

    return paradigm_per_year


def aggregate_paradigms(metadata_filepath):
    '''
    Figure 3

    Aggregate the usage of each parallelization API.
    '''
    metadata = get_repo_metadata(metadata_filepath)
    count_paradigms = {'CUDA': 0, 'OpenCL': 0, 'OpenACC': 0, 'SYCL': 0, 
                            'TBB': 0, 'Cilk': 0, 'OpenMP': 0, 'MPI': 0}
    amount_repos = 0
    amount_repo_forked = 0
    amount_missed_repo = 0

    with open('analyzed_data/total_paradigms.json', 'r') as f:
        paradigm_per_repo = json.loads(f.read())

        for repo_name, paradigms in paradigm_per_repo.items():
            
            if repo_name not in metadata:
                amount_missed_repo += 1
                continue

            if metadata[repo_name]['fork']:
                amount_repo_forked += 1
                continue

            amount_repos += 1

            for paradigm, val in paradigms.items():
                if val:
                    count_paradigms[paradigm] += 1

        print(f'Amount of valid repos: {amount_repos}')
        print(f'Amount of repos not exist in metadata: {amount_missed_repo}')
        print(f'Amount of forked repos: {amount_repo_forked}')

        return count_paradigms
    

def cumulative_openmp(metadata_filepath):
    '''
    Figure 4

    Accumulate the usage of OpenMP API over the last decade
    '''
    total = 0
    openmp_over_time_cumulative = {}

    openmp_over_time = get_paradigms_over_time(['OpenMP'], metadata_filepath, avoid_fork=True, key='update_time')

    for year in range(2008, 2024):
        for month in range(12):
            y, m = year, month+1

            if y in openmp_over_time and m in openmp_over_time[y]:
                total += openmp_over_time[y][m]

            if y not in openmp_over_time_cumulative:
                openmp_over_time_cumulative[y] = {}

            openmp_over_time_cumulative[y][m] = total

    return openmp_over_time_cumulative


def get_paradigm_per_year(paradigms, metadata_filepath, key='creation_time'):
    '''
    Get the usage of a given parallelization API over the last decade.
    '''
    paradigm_per_year = {}
    paradigm_over_time = get_paradigms_over_time(paradigms, metadata_filepath, key=key)

    for year in paradigm_over_time:
        paradigm_per_year[year] = sum(paradigm_over_time[year].values())

    return paradigm_per_year


def get_paradigms_per_year(metadata_filepath):
    '''
    Figure 5

    Get the usage of each parallelization API per year
    '''
    paradigms_per_year = {}

    for paradigm in ['CUDA', 'OpenCL', 'OpenACC', 'SYCL', 'TBB', 'Cilk', 'OpenMP', 'MPI']:
        paradigms_per_year[paradigm] = get_paradigm_per_year([paradigm], metadata_filepath, key='update_time')

    return paradigms_per_year


def get_omp_mpi_usage(metadata_filepath):
    '''
    Figure 6

    Get the usage of OpenMP + MPI
    '''
    return get_paradigm_per_year(['OpenMP', 'MPI'], metadata_filepath, key='update_time')


def get_version_per_year(metadata_filepath):
    '''
    Figure 7

    Get the usage of each OpenMP version across the last decade
    '''
    versions_per_year = {}

    langs = ['Fortran', 'c', 'cpp']
    metadata = get_repo_metadata(metadata_filepath)

    for lang in langs:
        with open(f'analyzed_data/{lang}_versions.json', 'r') as f:
            versions_per_repo = json.loads(f.read())

            for repo, versions in versions_per_repo.items():
                if repo in metadata:
                    dt_object = metadata[repo]['update_time']

                    year = dt_object.year

                    if year not in versions_per_year:
                        versions_per_year[year] = {}

                    for version in versions['vers'].keys():
                        total = sum(versions['vers'][version].values())

                        if version not in versions_per_year[year]:
                            versions_per_year[year][version] = 0

                        versions_per_year[year][version] += total

    return versions_per_year


def get_loops():
    '''
    Figure 8

    get for-loop usage
    '''
    result = {}

    for lang in ['c', 'cpp', 'Fortran']:
        count_versions = aggregate_versions(lang)
        result[lang] = {'total_loop': count_versions['total_loop'],
                        'omp_for': count_versions['vers']['ver2.5']['do_' if lang=='Fortran' else 'for_']}
        
    return result


def get_scheduling():
    '''
    Figure 10

    Get scheduling  usage
    '''
    result = {}

    for lang in ['c', 'cpp', 'Fortran']:
        count_versions = aggregate_versions(lang)

        result[lang] = {'schedule_static': count_versions['vers']['ver2.5']['schedule_static'],
                        'schedule_dynamic': count_versions['vers']['ver2.5']['schedule_dynamic'],
                        'schedule_guided': count_versions['vers']['ver2.5']['schedule_guided'],
                        'schedule_auto': count_versions['vers']['ver3.0']['schedule_auto'],
                        'schedule_runtime': count_versions['vers']['ver2.5']['schedule_runtime']}
        
    return result


def aggregate_versions(lang):
    '''
    Figure 11

    Aggregate the usage of each OpenMP directive
    '''
    count_versions = {'total_loop': 0, 'vers': {'ver2.5': {}, 'ver3.0':{}, 'ver3.1':{}, 'ver4.0':{}, 'ver4.5':{}, 'ver5.0':{}, 'ver5.1':{}, 'ver5.2':{}} }

    with open(f'analyzed_data/{lang}_versions.json', 'r') as f:
        version_per_repo = json.loads(f.read())

        for versions in version_per_repo.values():

            count_versions['total_loop'] += versions['total_loop']

            for k in ['ver2.5', 'ver3.0', 'ver3.1', 'ver4.0', 'ver4.5', 'ver5.0', 'ver5.1', 'ver5.2']:
                for clause, amount in versions['vers'][k].items():
                    count_versions['vers'][k][clause] = amount if clause not in count_versions['vers'][k] else \
                                                                count_versions['vers'][k][clause]+amount
                    
        return count_versions
    