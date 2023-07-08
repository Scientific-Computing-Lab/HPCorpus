import re
from utils import is_for, is_omp_pragma


clauses_per_version = {
    'ver2.5': [(['parallel'],[]), (['sections'],[]), (['section'],[]), (['single'],[]), (['workshare'],[]), (['for'],[]), (['do'],[]), (['parallel', 'for'],[]), (['parallel', 'do'],[]), (['parallel', 'sections'],[]), (['parallel', 'workshare'],[]), (['master'],[]), (['critical'],[]), (['barrier'],[]), (['atomic'],[]), (['flush'],[]), (['ordered'],[]), (['threadprivate'],[]), (['default'],[]), (['shared'],[]), (['private'],[]), (['firstprivate'],[]), (['lastprivate'],[]), (['reduction'],[]), (['copyin'],[]), (['copyprivate'],[]), (['num_threads'],[]), (['schedule'],[]), (['schedule'],['static']), (['schedule'],['dynamic']), (['schedule'],['guided']), (['schedule'],['runtime']), (['nowait'],[])],
    'ver3.0': [(['task'],[]), (['taskwait'],[]), (['schedule'],['auto']), (['atomic', 'read'],[]), (['atomic', 'write'],[]), (['atomic', 'update'],[]), (['atomic', 'capture'],[])],
    'ver3.1': [(['taskyield'],[]), (['collapse'],[])],
    'ver4.0': [(['simd'],[]), (['simdlen'],[]), (['declare', 'simd'],[]), (['target'],[]), (['target', 'data'],[]), (['target', 'update'],[]), (['declare', 'target'],[]), (['teams'],[]), (['distribute'],[]), (['distribute', 'simd'],[]), (['target', 'teams'],[]), (['teams', 'distribute'],[]), (['teams', 'distribute', 'simd'],[]), (['target', 'teams', 'distribute'],[]), (['target', 'teams', 'distribute', 'simd'],[]), (['taskgroup'],[]), (['cancel'],[]), (['cancellation'],[]), (['map'],[]), (['declare', 'reduction'],[]), (['proc_bind'],[])],
    'ver4.5': [(['taskloop'],[]), (['taskloop', 'simd'],[]), (['target', 'enter', 'data'],[]), (['target', 'exit', 'data'],[]), (['depend'],[]), (['linear'],[]), (['defaultmap'],[]), (['if'],[])],
    'ver5.0': [(['declare', 'variant'],[]), (['requires'],[]), (['distribute', 'loop'],[]), (['loop'],[]), (['scan'],[]), (['allocate'],[]), (['taskloop', 'simd'],[]), (['parallel', 'loop'],[]), (['parallel', 'master'],[]), (['master', 'taskloop'],[]), (['master', 'taskloop', 'simd'],[]), (['parallel', 'master', 'taskloop'],[]), (['parallel', 'master', 'taskloop', 'simd'],[]), (['teams', 'loop'],[]), (['parallel', 'target'],[]), (['target', 'parallel', 'loop'],[]), (['target', 'simd'],[]), (['target', 'teams', 'loop'],[]), (['deobj'],[]), (['task_reduction'],[]), (['in_reduction'],[]), (['copyprivate'],[]), (['declare', 'mapper'],[])],
    'ver5.1': [(['dispatch'],[]), (['assume'],[]), (['nothing'],[]), (['error'],[]), (['masked'],[]), (['scope'],[]), (['tile'],[]), (['unroll'],[]), (['interop'],[]), (['parallel', 'masked'],[]), (['masked', 'taskloop'],[]), (['masked', 'taskloop', 'simd'],[]), (['parallel', 'masked', 'taskloop', 'simd'],[])],
    'ver5.2': [(['destroy'],[]), (['is_device_ptr'],[]), (['use_device_ptr'],[]), (['has_device_ptr'],[]), (['use_device_addr'],[]), (['initializer'],[]), (['inclusive'],[]), (['exclusive'],[]), (['enter'],[]), (['link'],[]), (['to'],[]), (['from'],[]), (['uniform'],[]), (['aligned'],[]), (['align'],[]), (['allocator'],[]), (['allocators'],[]), (['use_allocators'],[]), (['when'],[]), (['otherwise'],[]), (['metadirective'],[]), (['begin', 'metadirective'],[]), (['match'],[]), (['adjust_args'],[]), (['append_args'],[]), (['begin', 'declare', 'variant'],[]), (['novariants'],[]), (['nocontext'],[]), (['begin', 'declare', 'target'],[]), (['indirect'],[]), (['at'],[]), (['assumes'],[]), (['begin', 'assumes'],[]), (['severity'],[]), (['message'],[]), (['sizes'],[]), (['full'],[]), (['partial'],[]), (['nontemporal'],[]), (['safelen'],[]), (['filter'],[]), (['dist_schedule'],[]), (['bind'],[]), (['untied'],[]), (['mergeable'],[]), (['final'],[]), (['priority'],[]), (['grainsize'],[]), (['num_tasks'],[]), (['device_type'],[]), (['device'],[]), (['thread_limit'],[]), (['init'],[]), (['use'],[]), (['hint'],[]), (['nogroup'],[]), (['doacross'],[]), (['nogroup'],[])]
}


def parse_openmp_pragma(pragma):
    '''
    parse OpenMP pragma into meaningful representation

    Parameters:
        pragma: str - string indicating the pragma
    Result:
        A list containing tuples representing the clause and their arguments

    Example:
        input: '#pragma omp for private  (a,b,c) lastprivate(d) schedule(static:8)'
        output: [('pragma', ''), ('omp', ''), ('for', ''), ('private', 'a,b,c'), ('lastprivate', 'd'), ('schedule', 'static:8')]

    '''
    pragma = pragma + " "
    pattern = r'(\w+(\s*\(.*?\)|\s))'
    matches = re.findall(pattern, pragma)
    clauses = []
    
    for match in matches:
        clause = match[0].strip()

        if '(' in clause:
            clause = clause[:clause.find('(')].strip()
            args = match[1].strip()[1:-1]
            clauses.append((clause, args))
        else:
            clauses.append((clause, ''))
    
    return clauses


def update_versions(line, versions):
    '''
    Determine the version of OpenMP pragma 

    Parameters:
        code: str - line of code
        versions: dict - amount of each clause (per version)

    Return:
        None (updates the versions dictionary)
    '''
    line = line.lstrip()
    parsed_pragma = parse_openmp_pragma(line)

    for ver, clauses_combination in clauses_per_version.items():
        for clause_combination in clauses_combination:
            
            clauses, args = clause_combination
            arg = '' if len(args)==0 else args[0]
            key = '_'.join(clauses) + '_' + arg

            if all([any([(clause==pragma_clause and arg in pragma_args) for pragma_clause, pragma_args in parsed_pragma]) for clause in clauses]):
                versions[ver][key] = 1 if key not in versions[ver] else versions[ver][key]+1


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

    versions = {'ver2.5': {}, 'ver3.0':{}, 'ver3.1':{}, 'ver4.0':{}, 'ver4.5':{}, 'ver5.0':{}, 'ver5.1':{}, 'ver5.2':{}}

    for line in code.split('\n'):

        if is_for(line, is_fortran):
            total_loop += 1

        if is_omp_pragma(line, is_fortran):
            update_versions(line, versions)

    return total_loop, versions