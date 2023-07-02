import os
import json
from tqdm import tqdm

# corpus_dir = '/mnt/c/Users/tal74/Downloads/'
# dirs = ['c_220'] # 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']
# # dirs = ['Fortran/Fortran'] #, 'cpp1', 'cpp2', 'cpp3', 'cpp4', 'cpp5', 'c_0', 'c_40', 'c_70', 'c_100', 'c_140', 'c_180', 'c_220', 'c_260', 'c_300', 'c_340']


# repos = set()

# for dir in tqdm(dirs):
#     dir_path = os.path.join(corpus_dir, dir)

#     for file in tqdm(os.listdir(dir_path)):
#         file_path = os.path.join(dir_path, file)

#         with open(file_path, 'r') as f:
#             for sample in f:
                
#                 try:
#                     js = json.loads(sample.strip())
#                 except:
#                     continue

#                 # repo = js['repo_name'].split('/')
#                 repo = js['repo_name']
#                 repos.add(repo)


# with open('repos_c7.jsonl', 'w') as f:
#     for repo in repos:
#         r = repo.split('/')
#         f.write(json.dumps({'username': r[0], 'repo_name': r[1]}) + '\n')




repos = set()

files = ['repos_c1', 'repos_c2', 'repos_c3', 'repos_c4', 'repos_c5', 'repos_c6', 'repos_c7', 'repos_c8', 'repos_c9', 'repos_c10', 'repos', 'repos1', 'repos2', 'repos3', 'repos4', 'repos5']
corpus_dir = '/home/talkad/OpenMPdb/database_creator/visualization/hpcorpus_stats/repos'



for file in tqdm(files):
    dir_path = os.path.join(corpus_dir, f'{file}.jsonl')

    with open(dir_path, 'r') as f:
        for sample in f:
            js = json.loads(sample.strip())

            str = js['username']+'/'+js['repo_name']
            repos.add(str)

with open('hpcorpus_repos.jsonl', 'w') as f:
    for repo in repos:
        r = repo.split('/')
        f.write(json.dumps({'username': r[0], 'repo_name': r[1]}) + '\n')
