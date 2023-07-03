import re


redundant_line_comments_c = re.compile("\/\/.*")
redundant_line_comments_fortran = re.compile("![^\$].*$|^c.*$", re.MULTILINE)
redundant_multiline_comments_c = re.compile("\/\*.*?\*\/", re.MULTILINE|re.DOTALL)


def remove_comments(code, is_fortran):
    '''
    Remove comments from given code

    Parameters:
        code: str - code textual representation
        is_fortran: bool - whether the code is written in the Fortran language

    Result:
        clean code
    '''
    if is_fortran:
        code = redundant_line_comments_fortran.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)
    else:
        code = redundant_line_comments_c.sub("\n", code)
        code = redundant_multiline_comments_c.sub("\n", code)

    return code


def concat_lines(code, is_fortran):
    '''
    Concatenate sequential splitted lined

    Parameters:
        code: str - code textual representation
        is_fortran: bool - whether the code is written in the Fortran language

    Result:
        clean code
    '''
    split_token = '&' if is_fortran else '\\' 
    code_buffer = []
    concat = False

    for line in code.split('\n'):
        next_concat = line.rstrip().endswith(split_token)
        if concat:
            if next_concat:
                line = line.rstrip()[:-1] + " "

            code_buffer[-1] = code_buffer[-1].rstrip() + " " + line
        else:            
            if next_concat:
                line = line.rstrip()[:-1] + " "

            code_buffer.append(line)

        concat = next_concat

    return '\n'.join(code_buffer)


def is_for(line, is_fortran):
    '''
	Return true if the given line is the beginning of a for-loop
      
    Parameters:
        line: str - line of code
        is_fortran: bool - whether the code is written in the Fortran language

    Result:
        true if the given line is the beginning of a for-loop
    '''
    sub_line = line.lstrip() # remove redundant white spaces

    if is_fortran:
        return sub_line.startswith('do ')
    
    return sub_line.startswith('for') and sub_line[3:].lstrip().startswith('(')


def is_omp_pragma(line, is_fortran):
	'''
	Return true if the given line is a for-pragma
      
    Parameters:
        line: str - line of code
        is_fortran: bool - whether the code is written in the Fortran language

    Result:
        true if the given line is a for-pragma
    '''
	sub_line = line.lstrip() # remove redundant white spaces
	if is_fortran:
		return sub_line.startswith('!$') and 'omp' in line and 'end' not in line
	else:
		return sub_line.startswith('#pragma ') and ' omp ' in line


