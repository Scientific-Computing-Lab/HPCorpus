import os
from tqdm import tqdm

dir = '/home/talkad/OpenMPdb/database_creator/asd/c'
files = os.listdir(dir)
func_amount = 0

for file in tqdm(files):
    with open(os.path.join(dir, file), 'r') as f:
        for line in f:
            func_amount += 1

print('functions amount: ', func_amount)

# fortran : 369820
# cpp: x 5
# c: 2158080 x 10 x 3