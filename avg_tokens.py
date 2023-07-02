import os
import json
from tqdm import tqdm
import sys

sys.path.extend(['.','/home/talkad/OpenMPdb/tokenizer', '/home/talkad/OpenMPdb/database_creator/parsers/HPCorpus_parser'])
from tokenizer import Tokompiler, TokenizerBPE, ASTokenizer, DFGTokenizer
from convert_representation import generate_replaced

tokompiler = Tokompiler()
bpe = TokenizerBPE()
astTokenizer = ASTokenizer()
dfgTokenizer = DFGTokenizer()

# code = generate_replaced(code, lang=lang)
# print(tokompiler.tokenize(code, replaced=True, lang=lang))
# print(astTokenizer.tokenize(code, replaced=True, lang=lang))
# print(dfgTokenizer.tokenize(code, replaced=True, lang=lang))

dir = '/home/talkad/OpenMPdb/database_creator/asd/fortran'
files = os.listdir(dir)
num_samples, total_tokens = 0, 0

for file in tqdm(files):
    with open(os.path.join(dir, file), 'r') as f:
        for line in f:
            js = json.loads(line.strip())
            code = js['code']
            # code = generate_replaced(code, lang='fortran')

            tokens = astTokenizer.tokenize(code, lang='fortran')

            num_samples += 1
            total_tokens += len(tokens)

    print('avg: ', total_tokens/num_samples)

