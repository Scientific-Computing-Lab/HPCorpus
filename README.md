# HPCorpus - Statistical Information

This repository provides code to extract statistical information about parallelization APIs, with a primary focus on OpenMP. The parallelization APIs covered in this repository include Cuda, OpenCL, OpenACC, SYCL, TBB, Cilk, OpenMP, and MPI. The extracted information aims to assist scientists in understanding the practical use of parallelization APIs in the programming languages C, C++, and Fortran, which are widely known for their high-performance capabilities.

The data is shared by demand.

## Repository Structure
The repository is organized as follows:

- main.py: This script is responsible for iterating over the HPCorpus, extracting statistics per repository, and saving the results.
- parallel_paradigm.py: This module provides functionality to identify the parallelization APIs used in a given code.
- pragma_version.py: This module aggregates the usage of each OpenMP clause in each code and separates them by their respective OpenMP version.

## Usage
To run the code and extract the statistical information, follow these steps:

Update the ENV.json file with your system's path to the HPCorpus directory.

Run the following command: python main.py
