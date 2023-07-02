import os
import re
import json
from tqdm import tqdm

# clauses = ['nowait', 'private', 'firstprivate', 'lastprivate', 'shared', 'reduction', 'atomic', 'section', 'for', 'task', 'barrier', 'critical', 'flush', 'single', 'master', 'target', 'static_schedule', 'dynamic_schedule']
clauses = ['nowait', 'private', 'firstprivate', 'lastprivate', 'shared', 'reduction', 'atomic', 'section', 'do', 'task', 'barrier', 'critical', 'flush', 'single', 'master', 'target', 'parallel_for', 'static_schedule', 'dynamic_schedule', 'loop_total']


redundant_line_comments_c = re.compile("\/\/.*")
redundant_line_comments_fortran = re.compile("![^\$].*$|^c.*$", re.MULTILINE)
redundant_multiline_comments_c = re.compile("\/\*.*?\*\/", re.MULTILINE|re.DOTALL)


def remove_comments(code, lang='c'):
    if lang == 'fortran':
        code = redundant_line_comments_fortran.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)
    else:
        code = redundant_line_comments_c.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)

    return code


def is_for(line, lang='c'):
    '''
	Return true if the given line is the beginning of for-loop
	'''
    sub_line = line.lstrip() # remove redundant white spaces

    if lang == 'c':
        return sub_line.startswith('for') and sub_line[3:].lstrip().startswith('(')

    return sub_line.startswith('do ')


def is_omp_pragma(line, count, is_fortran):
	'''
	Return true if the given line is for-pragma
	'''
	sub_line = line.lstrip() # remove redundant white spaces
	if is_fortran:
		return sub_line.startswith('!$') and 'omp' in line and 'end' not in line
	else:
		return sub_line.startswith('#pragma ') and ' omp ' in line


def clauses_counter(line, clauses_dict, is_fortran):
	'''
	count each clause in line of code

	Precondition:
		clauses_dict is initiated with all possible clauses
	'''
	
	for clause in clauses[: -4]:
		if clause in line:
			clauses_dict[clause] += 1

	if 'schedule' in line:
		if 'static' in line:
			clauses_dict['static_schedule'] += 1
		if 'dynamic' in line:
			clauses_dict['dynamic_schedule'] += 1
			
	if is_fortran:
		if 'parallel ' in line and 'do' in line:
			clauses_dict['parallel_for'] += 1
	else:
		if 'parallel ' in line and 'for' in line:
			clauses_dict['parallel_for'] += 1


def scan_file(code, clauses_amount, count, is_fortran):
    lang = 'fortran' if is_fortran else 'c'
    code = remove_comments(code, lang=lang)
    code = code.lower()

    for line in code.split('\n'):
        count['line'] += 1
        if is_for(line, lang=lang):
            clauses_amount['loop_total'] += 1

        if is_omp_pragma(line, count, is_fortran):  # check if pragma
            count['res'] += 1
            clauses_counter(line, clauses_amount, is_fortran)



def iterate_jsons(json_dir, is_fortran=False):
    clauses_amount = {clause: 0 for clause in clauses}
    count = {}
    count['res'] = 0
    count['line'] = 0
    for json_file in tqdm(os.listdir(json_dir)):
        with open(os.path.join(json_dir, json_file), 'r') as f:
            for line in f:
                js = json.loads(line.strip())
                if 'content' not in js:
                    continue

                scan_file(js['content'], clauses_amount, count, is_fortran=is_fortran)
    print(count)
    return clauses_amount








    # for json_file in tqdm(os.listdir(json_dir)):
    #     with open(os.path.join(json_dir, json_file), 'r') as f:
	    
    #         for line in f:
    #             js = json.loads(line.strip())

    #             if 'content' not in js:
    #                 continue

    #             scan_file(js['content'], clauses_amount, count, is_fortran=is_fortran)
		
    # return clauses_amount


# clauses_amount = {clause: 0 for clause in clauses}
# code = """
# a = 20
# ! $ adsf
# !$omp parallel do private ! asdd
# do i = 1, 50
# ! omp
# end do

# /*
# ads
# adf
# adg */
# asc
# // aed
# """

# scan_file(code, clauses_amount, False)
# print(clauses_amount)

# print(iterate_jsons('/tier2/bgu/bigQuery_repos/c'))
# print(iterate_jsons('/tier2/bgu/bigQuery_repos/cpp'))
# print(iterate_jsons('/tier2/bgu/bigQuery_repos/Fortran', is_fortran=True))



# cpp:
# {"lastprivate": 8519, "task": 18270, "nowait": 2274, "barrier": 2728, "for": 89726, "parallel_for": 71428, "section": 9654, "simd": 54557, "single": 3469, "private": 34412, "dynamic_schedule": 3823, "reduction": 22875, "firstprivate": 10363, "master": 7871, "atomic": 5394, "flush": 1398, "static_schedule": 5628, "shared": 10194, "loop_total": 19868390, "critical": 8657, "target": 79076}

# c:
# {"lastprivate": 1623, "task": 4501, "nowait": 1008, "barrier": 2833, "for": 30185, "parallel_for": 22201, "section": 2501, "simd": 9877, "single": 1027, "private": 12885, "dynamic_schedule": 2093, "reduction": 3056, "firstprivate": 1908, "master": 1289, "atomic": 3652, "flush": 599, "static_schedule": 6168, "shared": 7712, "loop_total": 21936098, "critical": 4757, "target": 6248}

# fortran
# {"do": 17660, "lastprivate": 481, "task": 1695, "nowait": 12, "target": 2586, "barrier": 859, "parallel_for": 7949, "section": 979, "simd": 1252, "single": 584, "private": 16660, "reduction": 2819, "firstprivate": 1559, "master": 579, "atomic": 2085, "flush": 205, "static_schedule": 2164, "shared": 6016, "loop_total": 1203913, "critical": 1067, "dynamic_schedule": 806}


print(iterate_jsons('/mnt/c/Users/tal74/Downloads/Fortran/Fortran', is_fortran=True))