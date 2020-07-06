from bert_serving.client import BertClient
import config
import numpy as np
import re

bc = None

def get_concept_vector(concepts):
    global bc
    if not bc:
        if config.bert_client_ip:
            bc = BertClient(config.bert_client_ip)
        else:
            bc = BertClient()
    if isinstance(concepts, list):
        vecs = bc.encode(concepts)
        vecs = [vec / np.linalg.norm(vec, ord=2) for vec in vecs]
    if isinstance(concepts, str):
        vec = bc.encode([concepts])[0]
        vec = vec / np.linalg.norm(vec, ord=2)
    if vecs:
        return vecs
    assert Exception('Not supported BERT input')

def get_similarity(c1, c2):
    vec1, vec2 = get_concept_vector([c1, c2])
    return np.dot(vec1, vec2)

def load_data_vecs():
    candidates, vecs = [], []
    with open(config.tmp_middle_res, 'r', encoding='utf-8') as f:
        candidates = f.read().split('\n')
        vecs = get_concept_vector(candidates)
    vecs = np.array(vecs)
    print('Load data complete, candidate number: {}, vecs shape: {}'.format(len(candidates), vecs.shape))
    return candidates, vecs

def load_data_text():
    candidates, text = [], []
    with open(config.tmp_middle_res, 'r', encoding='utf-8') as f:
        candidates = f.read().split('\n')
    with open(config.input_text, 'r', encoding='utf-8') as f:
        text = re.sub('\xa3|\xae|\x0d', '', f.read()).lower()
        text = text.split('\n')
    print('Load data complete, candidate number: {}, text line number: {}'.format(len(candidates), len(text)))
    return candidates, text

def cal_vector_distance(vecs):
    print('Start calculate vector distance.')
    max_num = config.max_num
    t = config.threshold
    K = 768  # the same dimension as BERT Base, reduce space cost
    N = vecs.shape[0]
    M = N if max_num == -1 else min(N, max_num)
    edges = [[] for i in range(N)]
    i = 0
    while i < N:
        weight = np.dot(vecs[i:i+K], vecs.T)
        sorted_index = np.argsort(-weight)[:, 0:M]
        for k in range(min(K, N-i)):
            for j in range(M):
                w = weight[k, sorted_index[k, j]]
                tar = sorted_index[k, j]
                if w > t:
                    edges[i+k].append([w, tar])
        i += min(K, N-i)
        print('Progress:', i/N)
    return edges