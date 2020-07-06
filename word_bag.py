from preprocess import *
import re
import config
from tqdm import tqdm
import jieba

def indexstr(str1,str2):
    '''查找指定字符串str1包含指定子字符串str2的全部位置，
    以列表形式返回'''
    lenth2=len(str2)
    lenth1=len(str1)
    indexstr2=[]
    i=0
    while str2 in str1[i:]:
        indextmp = str1.index(str2, i, lenth1)
        indexstr2.append(indextmp)
        i = (indextmp + lenth2)
    return indexstr2

def word_bag():
    concept_path = config.cluster_save_path
    context_path = config.input_text
    with open(context_path, 'r') as f:
        lines = f.readlines()
        context = ' '.join(lines)
    concept_json = json_loader(concept_path)
    prun_length = config.prun_length
    concept_json = concept_json[:prun_length]
    concept_name = [js['name'] for js in concept_json]
    concept_json_dict = {js['name']:js for js in concept_json}

    for name in tqdm(concept_name):
        posi = indexstr(context, name)
        concept_json_dict[name]['posi'] = posi

    concept_posi_list = []
    for concept, js in concept_json_dict.items():
        for posi in js['posi']:
            concept_posi_list.append((concept, posi))
    concept_posi_list = sorted(concept_posi_list, key=lambda x: x[1])

    for concept in concept_json_dict:
        concept_json_dict[concept]['pre'] = {}
        concept_json_dict[concept]['same'] = {}
        concept_json_dict[concept]['post'] = {}
        if config.word_cut_mode:
            concept_json_dict[concept]['word_cut'] = {}
    posi_l = len(context)
    l = len(concept_posi_list)
    bag_length = config.bag_length
    for i, (concept, posi) in tqdm(enumerate(concept_posi_list)):
        j = i + 1
        while j < l:
            temp_c, temp_p = concept_posi_list[j]
            j += 1
            if temp_p == posi:
                if temp_c not in concept_json_dict[concept]['same']:
                    concept_json_dict[concept]['same'][temp_c] = 1
                else:
                    concept_json_dict[concept]['same'][temp_c] += 1

            elif temp_p < posi + config.bag_length:
                if temp_c not in concept_json_dict[concept]['post']:
                    concept_json_dict[concept]['post'][temp_c] = 1
                else:
                    concept_json_dict[concept]['post'][temp_c] += 1
                if concept not in concept_json_dict[temp_c]['pre']:
                    concept_json_dict[temp_c]['pre'][concept] = 1
                else:
                    concept_json_dict[temp_c]['pre'][concept] += 1
            else:
                break
        if config.word_cut_mode:
            min_posi = max(0, posi - config.bag_length)
            max_posi = min(posi_l, posi + config.bag_length)
            text = context[min_posi: max_posi]
            text = jieba.cut(text)
            for w in text:
                if w not in concept_json_dict[concept]['word_cut']:
                    concept_json_dict[concept]['word_cut'][w] = 1
                else:
                    concept_json_dict[concept]['word_cut'][w] += 1
    result_json_list = [js for concept, js in concept_json_dict.items()]
    # print(result_json_list)
    json_dumper(config.save_word_bag, result_json_list)


if __name__ == '__main__':
    word_bag()