import os

# parsed baike context of seed concepts
baike_context = 'input_data/concept_baike/parsed_concept_baidu_1.json'
seed_folder_path = 'input_data/seeds'
context_folder_path = 'input_data/context'

# default paths
zh_list = 'processed_data/crawler_results/zh_list'
en_list = 'processed_data/crawler_results/en_list'
db = 'snippet.db'
cookie_paths = ['crawler/cookie/{}'.format(file) for file in os.listdir('crawler/cookie/')]

# tmp paths
tmp_input_text = 'tmp/input_text.txt'
tmp_middle_res = 'tmp/middle_res.txt'
result_path = 'processed_data/propagation_results/result.json'

# default paramters
proxy = {'http': 'http://localhost:8001', 'https': 'http://localhost:8001'}  # should change to your own proxy
bert_client_ip = None
input_text = 'input_data/context/baike_context'
input_seed = 'input_data/seeds/seed_concepts'
language = 'zh'
snippet_source = 'baidu'
times = None
max_num = None
threshold = None
decay = None
no_seed =  False

# Xlink related settings

url  =  "http://166.111.68.66:9068/EntityLinkingWeb/linkingSubmit.action"
lang = "zh" 
 # "zh" for extract Chinese concepts, "en" for English
folder_path = "input_data/context" 
file_name = "baike_context"
save_folder = "processed_data/xlink_results" 

rerank_result_path = "processed_data/rerank_results/rerank_result.json"

# clustering settings
num_clusters = 15
num_seed_clusters = 10
wordvector_path = "word_clustering/word_vectors/sgns.baidubaike.bigram-char"
cluster_concept_path = "processed_data/rerank_results/rerank_result.json"
cluster_save_path = "processed_data/cluster_results/cluster_result.json"

# word bag
prun_length = 1000
bag_length = 20
save_word_bag = 'processed_data/word_bag_results/word_bag.json'
word_cut_mode = True