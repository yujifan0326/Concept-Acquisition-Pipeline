import numpy as np
import json
import config
import pickle
import math
import confidence_propagation.algorithm_api as api
import tqdm

def tf_idf(candidates, text):
    n = len(candidates)
    score_list = np.zeros(n)
    for i in tqdm.tqdm(range(n)):
        c = candidates[i]
        tf = max([len(t.split(c))-1 for t in text])
        idf = len([c in t for t in text])
        score_list[i] = tf / math.log(1+idf)
    return score_list

def get_result():
    candidates, text = api.load_data_text()
    score_list = tf_idf(candidates, text)
    sorted_list = np.argsort(-score_list)
    with open(config.result_path, 'w', encoding='utf-8') as f:
        for index in sorted_list:
            encode = json.dumps({'name': candidates[index], 'score': score_list[index]}, ensure_ascii=False)
            f.write(encode+'\n')
    print('Finished!')