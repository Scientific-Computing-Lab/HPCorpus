from utils import is_for, is_omp_pragma



def update_versions(line, versions, is_fortran):
    '''
    Determine the version of OpenMP pragma 

    Parameters:
        code: str - line of code
        versions: dict - amount of each clause (per version)
        is_fortran: bool - whether the code is written in the Fortran language

    Return:
        None (updates the versions dictionary)
    '''
    line = line.lstrip()
    #     version 5
    clauses = [clause for clause in ['requiers','loop', 'order(concurrent)', 'scan', 'inscan',  'mutexinoutset'] if clause in line]
    if 'atomic' in line and 'hint' in line:
        clauses.append('atomic_hint')
    if 'taskwait' in line and 'depend' in line:
        clauses.append('taskwait_depend')
    if 'task' in line:
        clauses += ['task_'+clause for clause in ['detach', 'affinity', 'in_reduction'] if clause in line]

    for clause in clauses:
        versions['5'][clause] = 1 if clause not in versions['5'] else versions['5'][clause]+1

    #     version 4.5
    clauses = [clause for clause in ['linear', 'simdlen', 'target', 'taskloop'] if clause in line]
    if 'task' in line and 'priority' in line:
        clauses.append('task_priority')
    if 'target' in line:
        clauses += ['target_'+clause for clause in ['private', 'nowait', 'depend', 'firstprivate', 'defaultmap'] if clause in line]
    
    for clause in clauses:
        versions['4.5'][clause] = 1 if clause not in versions['4.5'] else versions['4.5'][clause]+1

    #     version 4
    clauses = [clause for clause in ['cancel', 'taskgroup', 'proc_bind', 'simd'] if clause in line]
    if 'task' in line and 'depend' in line:
        clauses.append('task_depend')

    for clause in clauses:
        versions['4'][clause] = 1 if clause not in versions['4'] else versions['4'][clause]+1

    #     version 3
    clauses = [clause for clause in ['task', 'taskwait', 'schedule(auto)', 'taskyield'] if clause in line]
    if 'task' in line:
        clauses += ['task_'+clause for clause in ['final', 'mergeable'] if clause in line]
    if 'atomic' in line:
        clauses += ['atomic_'+clause for clause in ['read', 'write', 'capture', 'update'] if clause in line]
    
    for clause in clauses:
        versions['3'][clause] = 1 if clause not in versions['3'] else versions['3'][clause]+1

    #     version 2.5
    clauses = [clause for clause in [' private', 'section', 'barrier', 'nowait', 'critical', 'flush', 'single', 'master', 'firstprivate', 'lastprivate', 'shared', 'reduction', ' if', 'num_threads', 'collapse'] if clause in line]
    
    if 'schedule' in line:
        clauses += ['schedule_'+clause for clause in ['static', 'dynamic'] if clause in line]

    if (is_fortran and ' do' in line) or (not is_fortran and ' for' in line):
        clauses += ['for']

    if 'parallel' in line and ((is_fortran and ' do' in line) or (not is_fortran and ' for' in line)):
        clauses += ['parallel_for']

    for clause in clauses:
        versions['2'][clause] = 1 if clause not in versions['2'] else versions['2'][clause]+1



def get_omp_version(code, is_fortran):
    '''
    Get the clauses versions found in a given code

    Parameters:
        code: str - code textual representation
        versions: dict - amount of each clause (per version)
        is_fortran: bool - whether the code is written in the Fortran language

    Return:
        Amount of for loops and OpenMP version statistics
    '''
    total_loop = 0
    versions = {'2': {}, '3':{}, '4':{}, '4.5':{}, '5':{}}

    for line in code.split('\n'):

        if is_for(line, is_fortran):
            total_loop += 1

        if is_omp_pragma(line, is_fortran):
            update_versions(line, versions, is_fortran)

    return total_loop, versions
