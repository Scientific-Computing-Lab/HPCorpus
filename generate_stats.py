from csv import DictReader
from datetime import datetime
import json


def get_repo_metadata(metadata_filepath):
    metadata = {}
    prefix = 'https://github.com/'
    suffix = '.git'

    with open(metadata_filepath, 'r') as f:
        dict_reader = DictReader(f)

        for line in list(dict_reader):
            metadata[line['URL'][len(prefix): -len(suffix)]] = {'creation_time': line['creation_time'], 'update_time': line['update_time']}

    return metadata


def get_paradigms_over_time(paradigm_list, metadata_filepath):
    repos_over_time = {}

    langs = ['Fortran', 'c', 'cpp']
    metadata = get_repo_metadata(metadata_filepath)

    for lang in langs:
        with open(f'{lang}_paradigms.json', 'r') as f:
            paradigm_per_repo = json.loads(f.read())

            for repo, paradigms in paradigm_per_repo.items():
                if repo in metadata and all([val for paradigm ,val in paradigms.items() if paradigm in paradigm_list]):
                    dt_object = datetime.strptime(metadata[repo]['update_time'], '%Y-%m-%dT%H:%M:%SZ')

                    year = dt_object.year
                    month = dt_object.month

                    if year not in repos_over_time:
                        repos_over_time[year] = {}

                    if month not in repos_over_time[year]:
                        repos_over_time[year][month] = 0

                    repos_over_time[year][month] += 1

    return repos_over_time


def cumulative_openmp(metadata_filepath):
    total = 0
    openmp_over_time_cumulative = {}

    openmp_over_time = get_paradigms_over_time(['OpenMP'], metadata_filepath)

    for year in range(2012, 2023):
        for month in range(12):
            y, m = year, month+1

            if y in openmp_over_time and m in openmp_over_time[y]:
                total += openmp_over_time[y][m]

            if y not in openmp_over_time_cumulative:
                openmp_over_time_cumulative[y] = {}

            openmp_over_time_cumulative[y][m] = total

    return openmp_over_time_cumulative


def get_paradigm_per_year(paradigm, metadata_filepath):
    paradigm_per_year = {}
    paradigm_over_time = get_paradigms_over_time([paradigm], metadata_filepath)

    for year in paradigm_over_time:
        paradigm_per_year[year] = sum(paradigm_over_time[year].values())

    return paradigm_per_year


def get_version_per_year(metadata_filepath):
    versions_per_year = {}

    langs = ['Fortran', 'c', 'cpp']
    metadata = get_repo_metadata(metadata_filepath)

    for lang in langs:
        with open(f'{lang}_versions.json', 'r') as f:
            versions_per_repo = json.loads(f.read())

            for repo, versions in versions_per_repo.items():
                if repo in metadata:
                    dt_object = datetime.strptime(metadata[repo]['update_time'], '%Y-%m-%dT%H:%M:%SZ')

                    year = dt_object.year

                    if year not in versions_per_year:
                        versions_per_year[year] = {}

                    for version in versions['vers'].keys():
                        total = sum(versions['vers'][version].values())

                        if version not in versions_per_year[year]:
                            versions_per_year[year][version] = 0

                        versions_per_year[year][version] += total

    return versions_per_year


def reduce_paradigms(lang):
    count_paradigms = {'CUDA': 0, 'OpenCL': 0, 'OpenACC': 0, 'SYCL': 0, 
                                          'TBB': 0, 'Cilk': 0, 'OpenMP': 0, 'MPI': 0}

    with open(f'{lang}_paradigms.json', 'r') as f:
        paradigm_per_repo = json.loads(f.read())

        for paradigms in paradigm_per_repo.values():
            for paradigm, val in paradigms.items():
                if val:
                    count_paradigms[paradigm] += 1

        return count_paradigms


def reduce_versions(lang):
    count_versions = {'total_loop': 0, 'vers': {'2': {}, '3':{}, '4':{}, '4.5':{}, '5':{}} }

    with open(f'{lang}_versions.json', 'r') as f:
        version_per_repo = json.loads(f.read())

        for versions in version_per_repo.values():

            count_versions['total_loop'] += versions['total_loop']

            for k in versions['vers'].keys():
                for clause, amount in versions['vers'][k].items():
                    count_versions['vers'][k][clause] = amount if clause not in count_versions['vers'][k] else \
                                                                count_versions['vers'][k][clause]+amount
                    
        return count_versions
