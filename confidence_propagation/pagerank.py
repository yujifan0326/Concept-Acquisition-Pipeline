import numpy as np
import json
import config
import pickle
import math
import confidence_propagation.algorithm_api as api
import tqdm

def pagerank(candidates, text):
    n = len(candidates)
    if config.no_seed:
        score_list = np.ones(1)
        tot = n
    else:
        score_list = np.zeros(n)
        with open(config.input_seed, 'r', encoding='utf-8') as f:
            seed_set = set([seed.strip() for seed in f.read().split('\n')])
        tot = 0
        for i, c in enumerate(candidates):
            if c in seed_set:
                score_list[i] = 1.0
                tot += 1
    print('Seed number in candidates:', tot)
    mat = np.zeros((n, n))
    for t in tqdm.tqdm(text):
        g = []
        for i in range(n):
            if candidates[i] in t:
                g.append(i)
        for p1 in g:
            for p2 in g:
                mat[p1, p2] += 1.0
    for i in range(n):
        mat[i] /= np.sum(mat[i])
    for i in tqdm.tqdm(range(config.times)):
        score_list = np.matmul(score_list, mat)
    return score_list

def get_result():
    candidates, text = api.load_data_text()
    score_list = pagerank(candidates, text)
    sorted_list = np.argsort(-score_list)
    with open(config.result_path, 'w', encoding='utf-8') as f:
        for index in sorted_list:
            encode = json.dumps({'name': candidates[index], 'score': score_list[index]}, ensure_ascii=False)
            f.write(encode+'\n')
    print('Finished!')