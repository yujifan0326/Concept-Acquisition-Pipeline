import numpy as np
import json
import config
import pickle
import math
import confidence_propagation.algorithm_api as api
import tqdm

def average_dis(candidates, vecs):
    seed_set = set()
    n = len(candidates)
    if config.no_seed:
        seed_vecs = [vec for vec in vecs]
        tot = n
    else:
        with open(config.input_seed, 'r', encoding='utf-8') as f:
            seed_set = set([seed.strip() for seed in f.read().split('\n')])
        tot = 0
        seed_vecs = []
        for i, c in enumerate(candidates):
            if c in seed_set:
                seed_vecs.append(vecs[i])
                tot += 1
    print('Seed number in candidates:', tot)
    score_list = np.zeros(n)
    for i in tqdm.tqdm(range(n)):
        score_list[i] = np.mean([np.dot(vecs[i], vec) for vec in seed_vecs])
    return score_list

def get_result():
    candidates, vecs = api.load_data_vecs()
    score_list = average_dis(candidates, vecs)
    sorted_list = np.argsort(-score_list)
    with open(config.result_path, 'w', encoding='utf-8') as f:
        print(config.result_path)
        for index in sorted_list:
            encode = json.dumps({'name': candidates[index], 'score': score_list[index]}, ensure_ascii=False)
            f.write(encode+'\n')
    print('Finished!')