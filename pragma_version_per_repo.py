import os
import json
import pickle
import pandas as pd
from tqdm import tqdm
import timeout_decorator


corpus_dir = '/mnt/c/Users/tal74/Downloads/'
# # dirs = ['c_220'] # 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
# # dirs = ['Fortran/Fortran', 'cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5', 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
# dirs = [  'c_220', 'c_260', 'c_300', 'c_340']



def get_omp_version(line, res, is_fortran):
    '''
        For a given pragma, determine the version of OpenMP it is related
    '''
    if (is_fortran and line.startswith('!$omp')) or (not is_fortran and line.startswith('#pragma')):
        if any([(clause in line) for clause in ['requires','loop', 'order(concurrent)', 'scan', 'inscan',  'mutexinoutset', 'taskloop']]) or ('atomic' in line and any([clause in line for clause in ['hint']])) or ('taskwait' in line and 'depend' in line)  or ('task' in line and any([clause in line for clause in ['detach', 'affinity', 'in_reduction']])):
            res['5'] += 1

        elif any([(clause in line) for clause in ['linear', 'simdlen']]) or ('task' in line and 'priority' in line) or ('target' in line and any([clause in line for clause in ['private', 'nowait', 'is_device_ptr', 'depend', 'firstprivate', 'defaultmap']])):
            res['4.5'] += 1
        elif any([(clause in line) for clause in ['cancel', 'taskgroup', 'proc_bind', 'target', 'simd']])  or ('task' in line and any([clause in line for clause in ['depend']])):
            res['4'] += 1
        elif any((clause in line) for clause in ['task', 'collapse', 'taskwait', 'schedule(auto)', 'taskyield']) or ('atomic' in line and any([clause in line for clause in ['read', 'write', 'capture', 'update']])) or ('task' in line and any([clause in line for clause in ['final', 'mergeable']])) :
            res['3'] += 1
        else:
            res['2'] += 1
    

@timeout_decorator.timeout(30)
def iterate_code(code, versions, is_fortran):

    for line in code.split('\n'):
        l = line.lstrip().lower()
        get_omp_version(l, versions, is_fortran)


def save_versions(dir, is_fortran=False):
    repos = {}
    dir_path = os.path.join(corpus_dir, dir)

    for file in tqdm(os.listdir(dir_path)):
        file_path = os.path.join(dir_path, file)

        with open(file_path, 'r') as f:
            for sample in f:
                
                try:
                    js = json.loads(sample.strip())
                except:
                    continue

                if 'content' not in js:
                    continue

                versions = {'2': 0, '3': 0, '4': 0, '4.5': 0, '5': 0}
                repo_name = js['repo_name']
                code = js['content']
                code = code.lower()

                try:
                    iterate_code(code, versions, is_fortran)
                except timeout_decorator.timeout_decorator.TimeoutError as e:
                    print(e)

                if repo_name not in repos:
                    repos[repo_name] = {'2': 0, '3': 0, '4': 0, '4.5': 0, '5': 0}

                for ver, amount in versions.items():
                    repos[repo_name][ver]  += amount

    save_dir = dir.replace('/', '_')
    with open(f'{save_dir}.json', 'w') as f:
        f.write(json.dumps(repos))



# for dir in dirs:
#     save_versions(dir, is_fortran=False)






## union 
total_repos = {}

files = ['Fortran_Fortran', 'cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5', 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
corpus_dir = '/home/talkad/OpenMPdb/database_creator/visualization/hpcorpus_stats/openmp_versions'

for file in tqdm(files):
    dir_path = os.path.join(corpus_dir, f'{file}.json')

    with open(dir_path, 'r') as f:
        repos = json.loads(f.read())
        
        for repo_name, versions in repos.items():
            if repo_name not in total_repos:
                total_repos[repo_name] = versions
            else:
                for version, val in versions.items():
                    total_repos[repo_name][version] += val

with open('hpcorpus_versions.json', 'w') as f:
    f.write(json.dumps(total_repos))

