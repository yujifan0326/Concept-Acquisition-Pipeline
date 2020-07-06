import config
import argparse
import os
import confidence_propagation.preprocess as preprocess
import confidence_propagation.graph_propagation as graph_propagation
import confidence_propagation.average_distance as average_distance
import confidence_propagation.tf_idf as tf_idf
import confidence_propagation.pagerank as pagerank
import crawler.snippet_crawler as crawler
def main():
    parser = argparse.ArgumentParser(description='process some parameters, the whole parameters are in config.py')
    parser.add_argument('-task', type=str, default='expand', choices=['extract', 'expand'], help='extract | expand', required=True)
    parser.add_argument('--input_text', '-it', default=config.input_text,type=str, help='the text file for concept extraction task')
    parser.add_argument('--input_seed', '-is',default=config.input_seed, type=str, help='the seed file for concept extraction | expansion task')
    parser.add_argument('--language', '-l', default='zh', type=str, choices=['zh', 'en'], help='zh | en', required=True)
    parser.add_argument('--snippet_source', '-ss', default='baidu', type=str, choices=['baidu', 'google', 'bing'], help='baidu | google | bing')
    parser.add_argument('--times', '-t', default=10, type=int, help='iteration times for graph propagation algorithm')
    parser.add_argument('--max_num', '-m', default=-1, type=int, help='maximun number for outgoing edges of each node, "-1" means unlimited')
    parser.add_argument('--decay', '-d', default=0.8, type=float, help='decay for graph propagation algorithm')
    parser.add_argument('--threshold', '-th', default=0.7, type=float, help='similarity threshold for graph edges')
    parser.add_argument('--no_seed', '-ns', action='store_true', help='every candidate in text will be a seed')
    parser.add_argument('--noun_filter', '-nf', action='store_true', help='remove non noun candidates')
    parser.add_argument('--result', '-r', default=config.result_path, type=str, help='result file path')
    parser.add_argument('--algorithm', '-a', type=str, default='graph_propagation', choices=['graph_propagation', 'average_distance', 'tf_idf', 'pagerank'], help='graph_propagation | average_distance | tf_idf | pagerank')
    args = parser.parse_args()
    if not args.input_text and args.task == 'extract':
        raise Exception('concept extraction task need input_text')
    if not args.input_seed and args.task == 'expand':
        raise Exception('concept extraction task need input_text')
    if not args.no_seed and not args.input_seed:
        raise Exception('seed config error')
    config.input_text = args.input_text
    config.input_seed = args.input_seed
    config.language = args.language
    config.snippet_source = args.snippet_source
    config.times = args.times
    config.max_num = args.max_num
    config.decay = args.decay
    config.threshold = args.threshold
    config.no_seed = True if args.no_seed else False
    config.noun_filter = True if args.noun_filter else False
    config.result_path = args.result
    
    if args.task == 'expand':
        text = []
        with open(config.input_seed, 'r', encoding='utf-8') as f:
            for line in f.read().split('\n'):
                if line != '':
                    text.append(crawler.get_snippet(line))
        config.input_text = config.tmp_input_text
        with open(config.input_text, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text))
    preprocess.get_candidates()
    if args.algorithm == 'graph_propagation':
        graph_propagation.get_result()
    if args.algorithm == 'average_distance':
        average_distance.get_result()
    if args.algorithm == 'tf_idf':
        tf_idf.get_result()
    if args.algorithm == 'pagerank':
        pagerank.get_result()

if __name__ == '__main__':
    main()