import os
import json
import pickle
import pandas as pd
from tqdm import tqdm
import re


redundant_line_comments_c = re.compile("\/\/.*")
redundant_line_comments_fortran = re.compile("![^\$].*$|^c.*$", re.MULTILINE)
redundant_multiline_comments_c = re.compile("\/\*.*?\*\/", re.MULTILINE|re.DOTALL)


def remove_comments(code, is_fortran):
    if is_fortran:
        code = redundant_line_comments_fortran.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)
    else:
        code = redundant_line_comments_c.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)

    return code


def get_omp_version_per_clause(line, res, is_fortran):
    '''
        For a given pragma, determine the version of OpenMP it is related
    '''
    if (is_fortran and line.startswith('!$') and 'omp' in line and 'end' not in line) or (not is_fortran and line.startswith('#pragma ') and ' omp ' in line):
        # count['res'] += 1
        # if 'private' in line:
        #     res['2']['private'] = 1 if 'private' not in res['2'] else res['2']['private']+1

        if any([(clause in line) for clause in ['requires','loop', 'order(concurrent)', 'scan', 'inscan',  'mutexinoutset', 'taskloop']]) or ('atomic' in line and any([clause in line for clause in ['hint']])) or ('taskwait' in line and 'depend' in line)  or ('task' in line and any([clause in line for clause in ['detach', 'affinity', 'in_reduction']])):
            clauses = [clause for clause in ['requires','loop', 'order(concurrent)', 'scan', 'inscan',  'mutexinoutset', 'taskloop'] if clause in line]
            if 'atomic' in line and 'hint' in line:
                clauses.append('atomic_hint')
            if 'taskwait' in line and 'depend' in line:
                clauses.append('taskwait_depend')
            if 'task' in line:
                clauses += ['task_'+clause for clause in ['detach', 'affinity', 'in_reduction'] if clause in line]

            for clause in clauses:
                res['5'][clause] = 1 if clause not in res['5'] else res['5'][clause]+1

        if any([(clause in line) for clause in ['linear', 'simdlen']]) or ('task' in line and 'priority' in line) or ('target' in line and any([clause in line for clause in ['private', 'nowait', 'is_device_ptr', 'depend', 'firstprivate', 'defaultmap']])):
            clauses = [clause for clause in ['linear', 'simdlen'] if clause in line]
            if 'task' in line and 'priority' in line:
                clauses.append('task_priority')
            if 'target' in line:
                clauses += ['target_'+clause for clause in ['private', 'nowait', 'is_device_ptr', 'depend', 'firstprivate', 'defaultmap'] if clause in line]
            
            for clause in clauses:
                res['4.5'][clause] = 1 if clause not in res['4.5'] else res['4.5'][clause]+1

        if any([(clause in line) for clause in ['cancel', 'taskgroup', 'proc_bind', 'target', 'simd']])  or ('task' in line and any([clause in line for clause in ['depend']])):
            clauses = [clause for clause in ['cancel', 'taskgroup', 'proc_bind', 'target', 'simd'] if clause in line]
            if 'task' in line and 'depend' in line:
                clauses.append('task_depend')

            for clause in clauses:
                res['4'][clause] = 1 if clause not in res['4'] else res['4'][clause]+1

        if any((clause in line) for clause in ['task', 'collapse', 'taskwait', 'schedule(auto)', 'taskyield']) or ('atomic' in line and any([clause in line for clause in ['read', 'write', 'capture', 'update']])) or ('task' in line and any([clause in line for clause in ['final', 'mergeable']])) :
            clauses = [clause for clause in ['task', 'collapse', 'taskwait', 'schedule(auto)', 'taskyield'] if clause in line]
            if 'task' in line:
                clauses += ['task_'+clause for clause in ['final', 'mergeable'] if clause in line]
            if 'atomic' in line:
                clauses += ['atomic_'+clause for clause in ['read', 'write', 'capture', 'update'] if clause in line]
            
            for clause in clauses:
                res['3'][clause] = 1 if clause not in res['3'] else res['3'][clause]+1

        if any((clause in line) for clause in ['private', 'firstprivate', 'shared', 'reduction', 'lastprivate', 'if', 'num_threads', 'schedule']):
            clauses = [clause for clause in ['private', 'firstprivate', 'lastprivate' 'shared', 'reduction', ' if', 'num_threads'] if clause in line]
            
            if 'schedule' in line:
                clauses += ['schedule_'+clause for clause in ['static', 'dynamic'] if clause in line]

            for clause in clauses:
                res['2'][clause] = 1 if clause not in res['2'] else res['2'][clause]+1



def iterate_jsons(dirs, is_fortran=False):
    versions = {'2': {}, '3':{}, '4':{}, '4.5':{}, '5':{}}

    for dir in dirs:
        json_dir = os.path.join('/mnt/c/Users/tal74/Downloads', dir)

        for json_file in tqdm(os.listdir(json_dir)):
            with open(os.path.join(json_dir, json_file), 'r') as f:
                for line in f:
                    try:
                        js = json.loads(line.strip())
                    except:
                        continue

                    if 'content' not in js:
                        continue

                    code = js['content']
                    code = remove_comments(code, is_fortran)

                    for line in code.split('\n'):
                        l = line.lstrip().lower()

                        get_omp_version_per_clause(l, versions, is_fortran)

    return versions




# dirs =  ['Fortran/Fortran']
# dirs =  ['cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5']
# dirs =  ['c_0', 'c_40', 'c_70', 'c_100', 'c_140']
# dirs = ['c_180', 'c_220', 'c_260', 'c_300', 'c_340']

# print(iterate_jsons(dirs))


# c
# {'2': {'num_threads': 898, 'private': 6161, 'schedule_static': 2652, 'schedule_dynamic': 1040, 'firstprivate': 946, ' if': 452, 'reduction': 1404}, '3': {'task': 2019, 'taskwait': 308, 'collapse': 1384, 'atomic_write': 285, 'atomic_update': 78, 'atomic_read': 149, 'schedule(auto)': 22, 'atomic_capture': 193, 'taskyield': 8, 'task_final': 17, 'task_mergeable': 7}, '4': {'simd': 5159, 'target': 3124, 'taskgroup': 51, 'proc_bind': 59, 'task_depend': 154, 'cancel': 31}, '4.5': {'linear': 406, 'simdlen': 354, 'target_nowait': 73, 'target_depend': 21, 'target_private': 621, 'target_defaultmap': 41, 'target_firstprivate': 219, 'task_priority': 10, 'target_is_device_ptr': 15}, '5': {'loop': 817, 'taskloop': 706, 'order(concurrent)': 88, 'mutexinoutset': 7, 'task_detach': 18, 'scan': 98, 'inscan': 49, 'task_in_reduction': 36, 'taskwait_depend': 5, 'task_affinity': 41, 'requires': 10, 'atomic_hint': 11}}
# {'2': {'private': 6530, 'schedule_static': 3485, 'num_threads': 997, 'reduction': 1615, ' if': 918, 'firstprivate': 935, 'schedule_dynamic': 1005}, '3': {'collapse': 1076, 'task': 2436, 'taskwait': 325, 'taskyield': 21, 'atomic_update': 129, 'atomic_write': 267, 'atomic_read': 187, 'atomic_capture': 237, 'schedule(auto)': 11, 'task_final': 25, 'task_mergeable': 2}, '4': {'simd': 4452, 'target': 2880, 'cancel': 1209, 'proc_bind': 107, 'task_depend': 199, 'taskgroup': 442}, '4.5': {'linear': 473, 'simdlen': 413, 'target_is_device_ptr': 76, 'target_private': 283, 'target_firstprivate': 109, 'task_priority': 13, 'target_nowait': 71, 'target_depend': 47, 'target_defaultmap': 47}, '5': {'loop': 695, 'task_detach': 14, 'taskloop': 569, 'task_in_reduction': 52, 'requires': 53, 'order(concurrent)': 35, 'scan': 193, 'inscan': 96, 'mutexinoutset': 5, 'task_affinity': 3, 'atomic_hint': 24, 'taskwait_depend': 8}}
#  ===
# {'2': {' if': 1370, 'private': 12691, 'schedule_static': 6137, 'num_threads': 1895, 'schedule_dynamic': 2045, 'firstprivate': 1881, 'reduction': 3019}, '3': {'atomic_read': 336, 'collapse': 2460, 'atomic_write': 552, 'atomic_update': 207, 'schedule(auto)': 33, 'atomic_capture': 430, 'task_final': 42, 'task_mergeable': 9, 'task': 4455, 'taskwait': 633, 'taskyield': 29}, '4': {'simd': 9611, 'cancel': 1240, 'proc_bind': 166, 'task_depend': 353, 'target': 6004, 'taskgroup': 493}, '4.5': {'task_priority': 23, 'target_nowait': 144, 'target_private': 904, 'simdlen': 767, 'target_is_device_ptr': 91, 'linear': 879, 'target_firstprivate': 328, 'target_depend': 68, 'target_defaultmap': 88}, '5': {'inscan': 145, 'mutexinoutset': 12, 'taskwait_depend': 13, 'task_in_reduction': 88, 'atomic_hint': 35, 'order(concurrent)': 123, 'loop': 1512, 'task_detach': 32, 'task_affinity': 44, 'taskloop': 1275, 'scan': 291, 'requires': 63}}

# cpp
# {'2': {'schedule_static': 5628, 'private': 34412, ' if': 8419, 'firstprivate': 10363, 'reduction': 22875, 'num_threads': 4517, 'schedule_dynamic': 3823}, '3': {'collapse': 5168, 'task': 18270, 'task_final': 431, 'taskwait': 1012, 'atomic_update': 552, 'atomic_read': 242, 'atomic_write': 288, 'atomic_capture': 1497, 'schedule(auto)': 208, 'taskyield': 705, 'task_mergeable': 98}, '4': {'target': 79076, 'simd': 54557, 'proc_bind': 798, 'cancel': 988, 'taskgroup': 1113, 'task_depend': 455}, '4.5': {'target_private': 6732, 'target_firstprivate': 2609, 'linear': 4642, 'target_depend': 4124, 'target_is_device_ptr': 2503, 'target_nowait': 715, 'simdlen': 1224, 'target_defaultmap': 1688, 'task_priority': 475}, '5': {'requires': 115, 'loop': 11139, 'taskloop': 11074, 'task_in_reduction': 1331, 'order(concurrent)': 50, 'atomic_hint': 25, 'mutexinoutset': 12, 'scan': 341, 'inscan': 77, 'task_detach': 52, 'task_affinity': 96, 'taskwait_depend': 37}}

# fortran
# {'2': {'num_threads': 1039, 'private': 16660, 'schedule_dynamic': 806, 'schedule_static': 2164, 'firstprivate': 1559, 'reduction': 2819, ' if': 705}, '3': {'task': 1695, 'taskwait': 312, 'collapse': 4793, 'atomic_write': 263, 'atomic_read': 248, 'atomic_capture': 196, 'atomic_update': 209, 'task_final': 34, 'task_mergeable': 24, 'taskyield': 11, 'schedule(auto)': 15}, '4': {'target': 2586, 'simd': 1252, 'taskgroup': 233, 'cancel': 469, 'proc_bind': 86}, '4.5': {'linear': 452, 'target_defaultmap': 154, 'target_private': 87, 'simdlen': 97, 'target_nowait': 11, 'task_priority': 27, 'target_firstprivate': 42, 'target_is_device_ptr': 37}, '5': {'loop': 452, 'taskloop': 331, 'task_affinity': 38, 'requires': 80, 'task_detach': 38, 'atomic_hint': 50, 'task_in_reduction': 33, 'scan': 128, 'inscan': 75, 'order(concurrent)': 124, 'mutexinoutset': 2}}





