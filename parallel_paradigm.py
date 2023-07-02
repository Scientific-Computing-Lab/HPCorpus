import os
import json
from tqdm import tqdm
import re
import multiprocessing
import timeout_decorator


corpus_dir = '/mnt/c/Users/tal74/Downloads/'
# # dirs = ['c_220'] # 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
# # dirs = ['Fortran/Fortran', 'cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5', 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
dirs = ['c_180']


paradigms = {
    'CUDA': [r'^\W*#\W*include\W+<cuda.h>.*$'],
    'OpenCL': [r'^\W*#\W*include\W+<cl/cl.h>.*$'],
    'OpenACC': [r'^\W*#\W*include\W+<openacc.h>.*$'],
    'SYCL': [r'^\W*#\W*include\W+<cl/sycl.hpp>.*$'],
    'TBB': [r'^\W*#\W*include\W+<tbb/tbb.h>.*$'],
    'Cilk': [r'^\W*#\W*include\W+<cilk/cilk.h>.*$'],
    'OpenMP': [r'^\W*#\W*include\W+<omp.h>.*$', r'\W*use\W+omp_lib.*$'],
    'MPI': [r'^\W*#\W*include\W+<mpi.h>.*$', r'\W*use\W+mpi.*$']
}

@timeout_decorator.timeout(30)
def get_parallel_paradigms(code):
    matched_paradigms = []

    for paradigm, patterns in paradigms.items():
        for pattern in patterns:
            if re.search(pattern, code, re.MULTILINE):
                matched_paradigms.append(paradigm)
                break
    
    return matched_paradigms


def save_paradigms(dir):
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

                repo_name = js['repo_name']
                code = js['content']
                code = code.lower()

                try:
                    paradigms = get_parallel_paradigms(code)
                except timeout_decorator.timeout_decorator.TimeoutError as e:
                    print(e)
                    paradigms = []

                if repo_name not in repos:
                    repos[repo_name] = {'CUDA': False, 'OpenCL': False, 'OpenACC': False, 'SYCL': False, 
                                          'TBB': False, 'Cilk': False, 'OpenMP': False, 'MPI': False}
                if paradigms is None:
                    continue
                for paradigm in paradigms:
                    repos[repo_name][paradigm] = True

    save_dir = dir.replace('/', '_')
    with open(f'{save_dir}.json', 'w') as f:
        f.write(json.dumps(repos))


# pool = multiprocessing.Pool(processes=4)
# results = pool.map(save_paradigms, dirs)

# pool.close()
# pool.join()

# save_paradigms('c_180')



## union 
# total_repos = {}

# files = ['Fortran_Fortran', 'cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5', 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
# corpus_dir = '/home/talkad/OpenMPdb/database_creator/visualization/hpcorpus_stats'

# for file in tqdm(files):
#     dir_path = os.path.join(corpus_dir, f'{file}.json')

#     with open(dir_path, 'r') as f:
#         repos = json.loads(f.read())
        
#         for repo_name, paradigms in repos.items():
#             if repo_name not in total_repos:
#                 total_repos[repo_name] = paradigms
#             else:
#                 for paradigm, val in paradigms.items():
#                     total_repos[repo_name][paradigm] |= val

# with open('hpcorpus_paradigms.jsonl', 'w') as f:
#     f.write(json.dumps(total_repos))


counter = {'CUDA': 0, 'OpenCL': 0, 'OpenACC': 0, 'SYCL': 0, 
            'TBB': 0, 'Cilk': 0, 'OpenMP': 0, 'MPI': 0}

with open('hpcorpus_paradigms.jsonl') as f:
    repos = json.loads(f.read())

    for paradigms in tqdm(repos.values()):
        for paradigm, val in paradigms.items():
            if val:
                counter[paradigm] += 1

print(counter)
# {'CUDA': 409, 'OpenCL': 399, 'OpenACC': 47, 'SYCL': 11, 'TBB': 91, 'Cilk': 75, 'OpenMP': 4261, 'MPI': 2226}
# sum = 7519