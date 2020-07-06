import jieba
import numpy as np
import json
from tqdm import tqdm


def load_word_dict(file_path, word_vector_path):
    print('loading word vectors')
    with open(word_vector_path,'r') as f:
        info = f.readline().split(' ')
        voc_num, word_dim = int(info[0]), int(info[1])
        lines = f.readlines()
        word_dict = {}
        for line in tqdm(lines):
            line = line.split(' ')
            word = line[0]
            word_vec = np.array([float(i) for i in line[1:301]])
            word_dict[word] = word_vec
    print('load successfully!')
    return word_dict

def concept_rep(concept, word_dict):
    word_list = jieba.cut(concept)

    word_list = [word for word in word_list if word in word_dict]

    rep = np.mean([word_dict[word] for word in word_list], axis=0)
    return rep, word_list

def cos_sim(vector1, vector2):
    return np.sum(vector1 * vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

def list_eq(list1, list2):
    l = len(list1)
    for i in range(l):
        if not (list1[i] == list2[i]).all():
            return False
    return True
    

def K_means(concept_list, n_cluster, word_dict):
    vector_list = []
    for concept in concept_list:
        rep, word_list = concept_rep(concept, word_dict)
        if len(word_list) > 0:
            vector_list.append((concept, rep))
    centroids = [vector for concept, vector in vector_list[:n_cluster]]
    stop = False
    step_count = 0
    while not stop:
        cluster_result = [[] for i in range(n_cluster)]
        cluster_concepts = [[] for i in range(n_cluster)]
        for concept, vector in vector_list:
            max_sim, index = -1, -1
            for i, centroid in enumerate(centroids):
                sim = cos_sim(vector, centroid)
                if sim > max_sim:
                    max_sim = sim
                    index = i
            cluster_result[index].append(vector)
            cluster_concepts[index].append(concept)
        new_centroids = [np.mean(item, axis=0) for item in cluster_result]
        step_count += 1
        #np.array(new_centroids).all() == np.array(centroids).all() or
        if list_eq(new_centroids, centroids) or step_count > 100:
            stop = True
            print(step_count)
        centroids = new_centroids
        print([len(i) for i in cluster_concepts])
    return centroids, cluster_concepts