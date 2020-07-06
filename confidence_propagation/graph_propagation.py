import numpy as np
import json
import config
import pickle
import math
import confidence_propagation.algorithm_api as api
import tqdm

def init_score_list(candidates):
    n = len(candidates)
    if config.no_seed:
        score_list = np.ones(n)
        tot = n
    else:
        with open(config.input_seed, 'r', encoding='utf-8') as f:
            seed_set = set([seed.strip() for seed in f.read().split('\n')])
        score_list = np.zeros(n)
        tot = 0
        for i, c in enumerate(candidates):
            if c in seed_set:
                score_list[i] = 1.0
                tot += 1
    print('Seed number in candidates:', tot)
    return score_list

def calc_pow(x, y):
    if x > 0:
        return math.pow(x, y)
    else:
        return -math.pow(-x, y)

def one_round(score_list, edges):
    new_score_list = np.zeros(score_list.shape)
    for source, score in enumerate(score_list):
        if score != 0.0:
            for (weight, target) in edges[source]:
                s = score * weight
                new_score_list[target] += s
    new_score_list /= np.max(new_score_list)
    return new_score_list

def graph_propagation(score_list, edges):
    print('Start graph propagation.')
    final_score_list = score_list
    for i in tqdm.tqdm(range(config.times)):
        score_list = one_round(score_list, edges)
        final_score_list += score_list * calc_pow(config.decay, i)
    return final_score_list

def get_result():
    candidates, vecs = api.load_data_vecs()
    edges = api.cal_vector_distance(vecs)
    score_list = init_score_list(candidates)
    score_list = graph_propagation(score_list, edges)
    sorted_list = np.argsort(-score_list)
    with open(config.result_path, 'w', encoding='utf-8') as f:
        for index in sorted_list:
            encode = json.dumps({'name': candidates[index], 'score': score_list[index]}, ensure_ascii=False)
            f.write(encode+'\n')
    print('Finished!')
