import re
import nltk
import jieba
import jieba.posseg as pseg
import json
import config
import pickle

def segment(data):
    res = []
    for line in data:
        if config.language == 'en':
            tmp = nltk.word_tokenize(line)
            seg = nltk.pos_tag(tmp)
        if config.language == 'zh':
            tmp = pseg.cut(line)
            seg = [(t.word, t.flag) for t in tmp]
        res.append(seg)
    return res

def phrase_in_lists(lists, phrase):
    t1 = 0
    t2 = len(lists) - 1
    while t1 < t2:
        t3 = (t1 + t2) // 2
        if phrase > lists[t3]:
            t1 = t3 + 1
        else:
            t2 = t3
    if phrase == lists[t1]:
        return True
    else:
        return False

def is_noun(flag):
    if config.language == 'en':
        flag = re.sub('JJ[RS]?', 'JJ', flag)
        flag = re.sub('NN[SP(PS)]?', 'NN', flag)
        if re.match(r'^((@(JJ|NN))+|(@(JJ|NN))*(@(NN|IN))?(@(JJ|NN))*)@NN$', flag) is not None:
            return True
        else:
            return False
    if config.language == 'zh':
        if re.match(r'^(@(([av]?n[rstz]?)|l|a|v))*(@(([av]?n[rstz]?)|l))$', flag) is not None:
            return True
        else:
            return False

def filter(lists, data):
    res = []
    phrase_set = set([''])
    tot, tot2 = 0, 0
    for seg in data:
        n = len(seg)
        for i in range(n):
            for j in range(6):
                words = [s[0] for s in seg[i:i+j+1]]
                flags = [s[1] for s in seg[i:i+j+1]]
                phrase, flag = '', '@'+'@'.join(flags)
                if config.language == 'en':
                    phrase = ' '.join(words)
                if config.language == 'zh':
                    phrase = ''.join(words)
                if phrase not in phrase_set:
                    phrase_set.add(phrase)
                    if phrase_in_lists(lists, phrase):
                        if not config.noun_filter or is_noun(flag):
                            res.append(phrase)
                        tot2 += 1
                    tot += 1
    print('phrase number: {}, in lists number: {}, final number: {}'.format(tot, tot2, len(res)))
    with open(config.tmp_middle_res, 'w', encoding='utf-8') as f:
        f.write('\n'.join(res))

def get_candidates():
    if config.language == 'en':
        with open(config.en_list, 'r', encoding='utf-8') as f:
            lists = f.read().split('\n')
    if config.language == 'zh':
        with open(config.zh_list, 'r', encoding='utf-8') as f:
            lists = f.read().split('\n')
    print('load vocab list done.')
    with open(config.input_text, 'r', encoding='utf-8') as f:
        text = re.sub('\xa3|\xae|\x0d', '', f.read()).lower()
        data = text.split('\n')
        data = segment(data)
        filter(lists, data)
    print('preprocess done.')