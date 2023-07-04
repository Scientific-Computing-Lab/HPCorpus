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
                    if val:
                        repos[repo][par] = True

        with open('total_paradigms.json'.format(dir), 'w') as f:
            f.write(json.dumps(repos))


def get_repo_metadata(metadata_filepath):
    '''
    Load metadata - creation and last update time of each repo
    '''
    metadata = {}
    prefix = 'https://github.com/'
    suffix = '.git'

    with open(metadata_filepath, 'r') as f:
        dict_reader = DictReader(f)

        for line in list(dict_reader):
            creation_time = datetime.strptime(line['creation_time'], '%Y-%m-%dT%H:%M:%SZ')
            update_time = datetime.strptime(line['update_time'], '%Y-%m-%dT%H:%M:%SZ')

            metadata[line['URL'][len(prefix): -len(suffix)]] = {'creation_time': creation_time, 'update_time': update_time}

    return metadata


def get_paradigms_over_time(paradigm_list, metadata_filepath):
    '''
    Get the number of repositories that used different parallelization APIs per month.
    '''
    repos_over_time = {}

    metadata = get_repo_metadata(metadata_filepath)

    with open('analyzed_data/total_paradigms.json', 'r') as f:
        paradigm_per_repo = json.loads(f.read())

        for repo, paradigms in paradigm_per_repo.items():
            if repo in metadata and all([val for paradigm ,val in paradigms.items() if paradigm in paradigm_list]):
                dt_object = metadata[repo]['update_time']

                year = dt_object.year
                month = dt_object.month

                if year not in repos_over_time:
                    repos_over_time[year] = {}

                if month not in repos_over_time[year]:
                    repos_over_time[year][month] = 0

                repos_over_time[year][month] += 1

    return repos_over_time


def cumulative_openmp(metadata_filepath):
    '''
    Figure 5

    Accumulate the usage of OpenMP API over the last decade
    '''
    total = 0
    openmp_over_time_cumulative = {}

    openmp_over_time = get_paradigms_over_time(['OpenMP'], metadata_filepath)

    for year in range(2012, 2024):
        for month in range(12):
            y, m = year, month+1

            if y in openmp_over_time and m in openmp_over_time[y]:
                total += openmp_over_time[y][m]

            if y not in openmp_over_time_cumulative:
                openmp_over_time_cumulative[y] = {}

            openmp_over_time_cumulative[y][m] = total

    return openmp_over_time_cumulative


def get_paradigm_per_year(paradigms, metadata_filepath):
    '''
    Figure 6 + 7

    Get the usage of a given parallelization API over the last decade.
    '''
    paradigm_per_year = {}
    paradigm_over_time = get_paradigms_over_time(paradigms, metadata_filepath)

    for year in paradigm_over_time:
        paradigm_per_year[year] = sum(paradigm_over_time[year].values())

    return paradigm_per_year


def get_version_per_year(metadata_filepath):
    '''
    Figure 9

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


def aggregate_paradigms():
    '''
    Figure 3 + 4

    Aggregate the usage of each parallelization API.
    '''
    count_paradigms = {'CUDA': 0, 'OpenCL': 0, 'OpenACC': 0, 'SYCL': 0, 
                                          'TBB': 0, 'Cilk': 0, 'OpenMP': 0, 'MPI': 0}

    with open('analyzed_data/total_paradigms.json', 'r') as f:
        paradigm_per_repo = json.loads(f.read())

        for paradigms in paradigm_per_repo.values():
            for paradigm, val in paradigms.items():
                if val:
                    count_paradigms[paradigm] += val

        return count_paradigms
    

def aggregate_versions(lang):
    '''
    Figure 8 + 10

    Aggregate the usage of each OpenMP directive
    '''
    count_versions = {'total_loop': 0, 'vers': {'2': {}, '3':{}, '4':{}, '4.5':{}, '5':{}} }

    with open(f'analyzed_data/{lang}_versions.json', 'r') as f:
        version_per_repo = json.loads(f.read())

        for versions in version_per_repo.values():

            count_versions['total_loop'] += versions['total_loop']

            for k in ['2', '3', '4', '4.5', '5']:
                for clause, amount in versions['vers'][k].items():
                    count_versions['vers'][k][clause] = amount if clause not in count_versions['vers'][k] else \
                                                                count_versions['vers'][k][clause]+amount
                    
        return count_versions
    
