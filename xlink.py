import config
from tqdm import tqdm
import requests
import json

def xlink_extract(folder_path, file_name):
    file_path = folder_path + '/' + file_name
    url  = config.url
    with open(file_path,'r') as f:
        lines = f.readlines()
    concept_list = []
    l = len(lines)
    lines = [''.join(lines[i * 100: min((i+1)*100, l)]) for i in range(l // 100 + 1)]
    for text in tqdm(lines):
        data = {"text": text, "lang": config.lang}
        request_result = requests.post(url, data)
        link_result = json.loads(request_result.text)
        concept_list.extend([link['label'] for link in link_result['ResultList']])
    concept_dict = {}
    for concept in concept_list:
        if concept not in concept_dict:
            concept_dict[concept] = 1
        else:
            concept_dict[concept] += 1
    return concept_dict

def json_dumper(file_path, js):
    with open(file_path, 'w') as f:
        str_ = '\n'.join([json.dumps(student, ensure_ascii=False) for student in js])
        f.write(str_)

def xlink_main():
    concept_dict = xlink_extract(config.folder_path, config.file_name)
    js = sorted([{"name": concept, "freq": frac} for concept, frac in concept_dict.items()], key=lambda x: x['freq'], reverse=True)
    json_dumper(config.save_folder +'/' + config.file_name, js)

if __name__=='__main__':
    xlink_main()