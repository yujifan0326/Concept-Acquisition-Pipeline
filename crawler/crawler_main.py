from snippet_crawler import *
import json
import numpy as np
import pickle
import config
from tqdm import tqdm
import os
def json_loader(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        return [json.loads(item) for item in lines]

def json_dumper(save_path, json_list):
    with open(save_path, 'w') as f:
        str_ = '\n'.join([json.dumps(item, ensure_ascii=False) for item in json_list])
        f.write(str_)

file_path = '../processed_concept_baidu/xlink_result/parsed_concept_baidu_1'
save_path = '../processed_concept_baidu/crawled_data/xlink_baidu_1'
count = 0

if __name__=='__main__':
    jsons = json_loader(file_path)
    concept_list = [item['name'] for item in jsons]
    if os.path.exists(save_path):
        json_list = json_loader(save_path)
        json_dict = {item['name']:{'baidu': item['baidu'], 'bing': item['bing']} for item in json_list}
    else:
        json_dict = {}
    for concept in tqdm(concept_list[3139:]):
        if concept in json_dict:
            if json_dict[concept]['baidu'] == '':
                config.snippet_source = 'baidu'
                baidu = crawl_snippet(concept)
                json_dict[concept]['baidu'] = baidu
            if json_dict[concept]['bing'] == '':
                config.snippet_source = 'bing'
                bing = crawl_snippet(concept)
                json_dict[concept]['bing'] = bing
        else:
            config.snippet_source = 'baidu'
            baidu = crawl_snippet(concept)
            config.snippet_source = 'bing'
            bing = crawl_snippet(concept)
            json_dict[concept] = {'baidu': baidu, 'bing': bing}
        count += 1
        if count % 100 == 0:
            json_list = [{'name': concept, 'baidu': crawl['baidu'], 'bing': crawl['bing']} for concept, crawl in json_dict.items()]
            json_dumper(save_path, json_list)
            print('saved successfully!')
    json_list = [{'name': concept, 'baidu': crawl['baidu'], 'bing': crawl['bing']} for concept, crawl in json_dict.items()]
    json_dumper(save_path, json_list)
    print('saved successfully!')