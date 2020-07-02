import logging
import csv
import itertools
import argparse
import random
import json
import numpy as np
import copy

def load_json(filename, extract_fn):
    with open(filename) as f:
        for line in f:
            yield extract_fn(json.loads(line))

def precision(seeds, predicted, k):
    return len(seeds.intersection(predicted[:k])) / k

# Assumes seeds (train set and test set) should be ranked higher
def ap_at_k(seeds, predicted, n):
    predicted = predicted[:n]
    return sum(precision(seeds, predicted, k) * (thing in seeds) for k, thing in enumerate(predicted) if k > 0) / min(len(seeds), n-1)

def evaluate(filename, k, relevance_field_name=None):
    if relevance_field_name:
        evals = list(load_json(filename, lambda x: {'name': x['name'], 'score': x[relevance_field_name]}))
        predicted = [thing['name'] for thing in sorted(evals, key=lambda x: -x['score'])]
    else:
        predicted = [thing['name'] for thing in load_json(filename, lambda x: {'name': x['name']})]
    random_predicted = copy.copy(predicted)
    random.shuffle(random_predicted)
    if len(seeds.intersection(predicted)) < 30:
        logging.warning("Not enough seeds included in the list to be evaluated. This evaluation may not be accurate.")
    results = {}
    results[f'mAP@{k}'] = ap_at_k(seeds, predicted, k)
    results[f'p@{k}'] = precision(seeds, predicted, k)
    results[f'random_mAP@{k}'] = ap_at_k(seeds, random_predicted, k)
    results[f'random_p@{k}'] = precision(seeds, random_predicted, k)
    if args.ndcg:
        from sklearn.metrics import ndcg_score
        scores = np.array([thing['score'] for thing in evals])
        targets = np.array([thing['name'] in seeds for thing in evals])
        results[f'nDCG@{k}'] = ndcg_score([targets[:k]], [scores[:k]])
        random.shuffle(scores)
        results[f'random_nDCG@{k}'] = ndcg_score([targets[:k]], [scores[:k]])
    return results

def dump_to_csv(results, filename):
    new_results = {x[0]: {} for x in results}
    for (evaluated_filename, k), result in results.items():
        new_results[evaluated_filename][f'mAP@{k}'] = result[f'mAP@{k}']
        new_results[evaluated_filename][f'p@{k}'] = result[f'p@{k}']
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        keys = list(map(lambda x: f'{x[0]}@{x[1]}', itertools.product(['mAP', 'p'], config.topks)))
        writer.writerow(['algorithm'] + keys)
        for ef, result in new_results.items():
            writer.writerow([config.file2algo[ef]] + [f'{result[k]:.3f}' for k in keys])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate ranking of concepts with a list of relavent concepts (e.g. evaluate concept expansion with seed concepts). '
            'This file calculates mAP@k, precision@k (and nDCG@k if provided with scores).')
    parser.add_argument('-c', '--config', action='store_true', help='use config file for evaluating multiple algorithms, in Python, containing seed_filename, evaluated_filenames and ks')
    parser.add_argument('-s', '--seed_filename',
            help='Seed file: lines of json format. (concept order in this file does not matter). '
            'This file contains relevant concepts that should appear in the evaluated ranking. '
            'For example, seeds used in concept expansion. '
            'Each line is a dict with key `name`, whose value is the name of the concept. '
            'Example line: `{"name": "binary tree"}`.')
    parser.add_argument('-e', '--evaluated_filename',
            help='Evaluated ranking file: lines of json format (concept order in this file matters). '
            'Each line is a dict with key `name`, whose value is the name of the concept. '
            'If `score` argument is provided, json of each line is expeceted to contain another key `score`, whose value is the a positive score of the concept. '
            'Example line: `{"name": "binary tree", "score": 0.523148}`.')
    parser.add_argument('-k', '--topk', help='The `k` of mAP@k. Top k of ranking to be evaluated.')
    parser.add_argument('-r', '--relevance', help='key name for score in file to be evaluated')
    parser.add_argument('-n', '--ndcg', action='store_true',
            help='Enables nDCG computation. json of each line of `evaluated_filename` is expeceted to contain key `score`, whose value is the score of the concept.')
    args = parser.parse_args()
    assert args.config or (args.seed_filename and args.evaluated_filename and args.topk), \
            "Please specify either config file, or (seed_filename, evaluated_filename, topk), but not both"
    if args.config:
        import config
        config = config.Evaluation
        seed_filename = config.seed_filename
    else:
        seed_filename = args.seed_filename
    seeds = set(load_json(seed_filename, lambda x: x['name']))
    if args.config:
        import config
        config = config.Evaluation
        results = {}
        for (evaluated_filename, field_name), k in itertools.product(
                zip(config.evaluated_filenames, config.relevance_field_names),
                config.topks):
            result = evaluate(evaluated_filename, k, field_name)
            results[(evaluated_filename, k)] = result
        if config.dump_csv:
            dump_to_csv(results, config.dump_csv)
        print(results)
    else:
        print(evaluate(args.evaluated_filename, int(args.topk), args.relevance))
