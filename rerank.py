import config
from preprocess import preprocess, json_loader, json_dumper
from xlink import xlink_main
import os
import math

def result_loader():
    conf_result_path = config.result_path
    xlink_result_path = config.save_folder + '/' + config.file_name
    conf_js = json_loader(conf_result_path)
    xlink_js = json_loader(xlink_result_path)
    return conf_js, xlink_js

def intersect_rerank():
    conf_js, xlink_js = result_loader()
    xlink_concept_dict = {concept['name'] : concept['freq'] for concept in xlink_js}
    extraction_concept_dict = {concept['name'] : concept['score'] for concept in conf_js}
    intersect_dict = {concept: (xlink_concept_dict[concept], extraction_concept_dict[concept])for concept in xlink_concept_dict if concept in extraction_concept_dict}

    def filter_function(scores):
        frac, score = scores
        return math.log(frac) * max(score - 4, 0) 
    intersect_dict = {concept : filter_function(scores) for concept, scores in intersect_dict.items()}
    intersect_sorted = sorted(intersect_dict.items(), key=lambda x: x[1], reverse=True)
    json_dumper(config.rerank_result_path, dict(intersect_dict))

def union_rerank():
    conf_js, xlink_js = result_loader()
    xlink_concept_dict = {concept['name'] : concept['freq'] for concept in xlink_js}
    extraction_concept_dict = {concept['name'] : concept['score'] for concept in conf_js}
    intersect_dict = {concept: (xlink_concept_dict[concept], extraction_concept_dict[concept])for concept in xlink_concept_dict if concept in extraction_concept_dict}

    xlink_minus_extract = {concept: (xlink_concept_dict[concept], 0)for concept in xlink_concept_dict if concept not in extraction_concept_dict}

    extract_minus_xlink = {concept: (1, extraction_concept_dict[concept])for concept in extraction_concept_dict if concept not in xlink_concept_dict}

    union_dict = intersect_dict.copy()
    union_dict.update(extract_minus_xlink)
    union_dict.update(xlink_minus_extract)

    def filter_function(scores):
        frac, score = scores
        return math.log(frac) * score

    def list2jsonlist(concept_dict):
        return [{"name": concept, "freq":scores[0], "score": scores[1], "R": scores[2]} for concept, scores in concept_dict]

    union_dict = {concept : (scores[0], scores[1], filter_function(scores)) for concept, scores in union_dict.items()}
    union_sorted = sorted(union_dict.items(), key=lambda x: x[1][2], reverse=True)
    json_dumper(config.rerank_result_path, list2jsonlist(union_sorted))

if __name__=='__main__':
    # preprocess()
    # os.system('python confidence_propagation.py -l {} -task {}'.format('zh', 'extract'))
    # xlink_main()
    union_rerank()