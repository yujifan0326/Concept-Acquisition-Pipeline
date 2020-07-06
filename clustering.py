import config
from word_clustering.kmeans import *
from preprocess import json_loader, json_dumper

def sort_key(i, centroids, seed_centroids):
    mean_vec = centroids[i]
    max_sim = -1
    for c in seed_centroids:
        sim = cos_sim(c, mean_vec)
        if sim > max_sim:
            max_sim = sim
    return max_sim

def sort_concept(concept, seed_centroids):
    global word_dict
    mean_vec = concept_rep(concept, word_dict)[0]
    max_sim = -1
    for c in seed_centroids:
        sim = cos_sim(c, mean_vec)
        if sim > max_sim:
            max_sim = sim
    return max_sim

def clustering_main():
    json_list = json_loader(config.cluster_concept_path)
    concept_dict = {js['name']: js for js in json_list}
    concept_list = [js['name'] for js in json_list]
    
    centroids, cluster_concepts = K_means(concept_list, config.num_clusters, word_dict)
    with open(config.input_seed) as f:
        seeds = [word.strip() for word in f.readlines()]
    seed_centroids, seed_cluster_concepts = K_means(seeds, config.num_seed_clusters, word_dict)
    sorted_cluster_concepts_tuple = [(cluster,sort_key(i, centroids, seed_centroids)) for i, cluster in enumerate(cluster_concepts)]
    sorted_cluster_concepts_tuple = sorted(sorted_cluster_concepts_tuple, key = lambda x: x[1], reverse=True)
    sorted_cluster_concepts_tuple = [(sorted(concept_list, key = lambda x: sort_concept(x, seed_centroids), reverse=True), score)for concept_list, score in sorted_cluster_concepts_tuple]
    index = 1
    js_list = []
    for cluster, score in sorted_cluster_concepts_tuple:
        for concept in cluster:
            temp_js = concept_dict[concept]
            temp_js['cluster'] = index
            js_list.append(temp_js)
        index += 1
    json_dumper(config.cluster_save_path, js_list)
    print([(cluster[:5], score) for cluster, score in sorted_cluster_concepts_tuple])
    
if __name__=='__main__':
    word_dict = load_word_dict(config.cluster_concept_path ,config.wordvector_path)
    clustering_main()