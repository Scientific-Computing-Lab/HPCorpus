#!/usr/bin/python 

import os
import json
from utils import remove_comments, concat_lines


from pragma_version import get_omp_version
from parallel_paradigm import get_parallel_paradigms


def iterate_jsons(dir, vars, is_fortran=False):
    '''
    Iterate over HPCorpus and return stats

    Prameters:
        dir: str - programming langauge directory to be iterated
        vars: dict - environment variables
        is_fortran: bool - whether the code is written in the Fortran language

    Return:
        Save OpenMP versions and parallel paradigms statistics
    '''

    par_paradigms = {}
    omop_versions = {}
    dir_path = os.path.join(vars['HPCorpus_path'], dir)

    for json_file in os.listdir(dir_path):
        with open(os.path.join(dir_path, json_file), 'r') as f:
            for line in f:
                try:
                    js = json.loads(line.strip())
                except:
                    continue

                if 'content' not in js:
                    continue
                
                repo_name = js['repo_name']
                code = js['content']
                code = remove_comments(code, is_fortran)
                code = concat_lines(code, is_fortran)

                ### Parallel Paradigms ###
                paradigms = get_parallel_paradigms(code)

                if repo_name not in par_paradigms:
                    par_paradigms[repo_name] = {'CUDA': False, 'OpenCL': False, 'OpenACC': False, 'SYCL': False, 
                                          'TBB': False, 'Cilk': False, 'OpenMP': False, 'MPI': False}

                for paradigm in paradigms:
                    par_paradigms[repo_name][paradigm] = True
                ### Parallel Paradigms ###


                ### OpenMP versions ###
                total_loop, versions = get_omp_version(code.lower(), is_fortran)

                if repo_name not in omop_versions:
                    omop_versions[repo_name] = {'total_loop': 0, 'vers': {'2': {}, '3':{}, '4':{}, '4.5':{}, '5':{}} }

                omop_versions[repo_name]['total_loop'] += total_loop

                for ver in versions.keys():
                    for clause, amount in versions[ver].items():
                        omop_versions[repo_name]['vers'][ver][clause] = amount if clause not in omop_versions[repo_name]['vers'][ver] else \
                                                                                omop_versions[repo_name]['vers'][ver][clause] + amount
                ### OpenMP versions ###
    
    with open('{}_paradigms.json'.format(dir), 'w') as f:
        f.write(json.dumps(par_paradigms))

    with open('{}_versions.json'.format(dir), 'w') as f:
        f.write(json.dumps(par_paradigms))



if __name__ == '__main__':

    with open('ENV.json', 'r') as f:
        vars = json.loads(f.read())

    iterate_jsons('Fortran', vars, is_fortran=True)

