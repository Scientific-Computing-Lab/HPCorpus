import re


paradigms = {
    'CUDA': [r'^\W*#\W*include.*[^a-zA-Z]cuda\.h.*$', r'^.*cudaMalloc\(.*$', r'^.*cudaFree\(.*$', r'^.*cudaMemcpy\(.*$', r'^.*cudaMemset\(.*$'],
    'OpenCL': [r'^\W*#\W*include.*[^a-zA-Z]cl\.h.*$', r'^.*clCreateContext\(.*$', r'^.*clReleaseContext\(.*$', r'^.*clCreateCommandQueue\(.*$', r'^.*clBuildProgram\(.*$', r'^.*clReleaseKernel\(.*$'],
    'OpenACC': [r'^\W*#\W*pragma\W*acc.*$'],
    'SYCL': [r'^\W*#\W*include.*[^a-zA-Z]sycl.hpp.*$', r'^\W*using\W+namespace\W+sycl.*$', r'^.*sycl::.*$'],   #, r'^.*sycl::event.*$', r'^.*sycl::handler.*$', r'^.*sycl::program.*$', r'^.*sycl::queue.*$', r'^.*sycl::buffer.*$', r'^.*sycl::kernel.*$', r'^.*sycl::range*$', r'^.*sycl::accessor.*$'],
    'TBB': [r'^\W*#\W*include.*[^a-zA-Z]tbb\.h.*$', r'^\W*using\W+namespace\W+tbb.*$', r'^.*tbb::.*$'],  #, r'^.*tbb::parallel_for.*$', r'^.*tbb::parallel_reduce.*$', r'^.*tbb::parallel_invoke.*$', r'^.*tbb::parallel_sort.*$', r'^.*tbb::parallel_scan.*$', r'^.*tbb::concurrent_vector.*$', r'^.*tbb::task_group.*$'],
    'Cilk': [r'^\W*#\W*include.*[^a-zA-Z]cilk\.h.*$', r'^\W*using\W+namespace\W+cilk.*$', r'^.*cilk_spawn\(.*$', r'^.*cilk_sync\(.*$', r'^.*cilk_for\(.*$'],
    'OpenMP': [r'^\W*#\W*pragma\W*omp.*$', r'^\W*!\$\W*[omp|OMP].*$'],
    'MPI': [r'^\W*#\W*include.*[^a-zA-Z]mpi\.h.*$', r'^\W*use\W+mpi.*$', r'^.*MPI_Init\(.*$', r'^.*MPI_Finalize\(.*$', r'^.*MPI_Comm_rank\(.*$', r'^.*MPI_Send\(.*$', r'^.*MPI_Recv\(.*$', r'^.*MPI_Alltoall\(.*$', r'^.*MPI_Scatter\(.*$', r'^.*MPI_Gather\(.*$', r'^.*MPI_Reduce\(.*$', r'^.*MPI_Allreduce\(.*$', r'^.*MPI_Bcast\(.*$']
} 



def get_parallel_paradigms(code):
    '''
    Get parallel paradigms found in a given code

    Parameters:
        code: str - code textual representation
    Return:
        list of the parallel paradigm
    '''
    matched_paradigms = []

    for paradigm, patterns in paradigms.items():
        for pattern in patterns:

            if re.search(pattern, code, re.MULTILINE):
                matched_paradigms.append(paradigm)
                break
    
    return matched_paradigms


