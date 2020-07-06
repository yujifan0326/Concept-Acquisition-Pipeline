import os

# default paths
zh_list = 'data/zh_list'
en_list = 'data/en_list'
db = 'snippet.db'
cookie_paths = ['cookie/{}'.format(file) for file in os.listdir('cookie/')]

# tmp paths
tmp_input_text = 'tmp/input_text.txt'
tmp_middle_res = 'tmp/middle_res.txt'
result_path = 'tmp/result.json'

# default paramters
proxy = {'http': 'http://localhost:8001', 'https': 'http://localhost:8001'}  # should change to your own proxy
bert_client_ip = None
input_text = None
input_seed = None
language = None
snippet_source = 'baidu'
times = None
max_num = None
threshold = None
decay = None
no_seed =  False
