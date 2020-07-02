# Concept Acquisition Pipeline

## 介绍/Introduction 

本项目由清华大学知识工程实验室维护，用于为特定领域构建科学概念/数据集。本项目设计了一个从少量文本出发，使用概念抽取，实体链接，概念扩展，交叉验证等的流程，用于获取高质量的大规模概念集。

项目的流程如下图所示，包含以下主要环节：

* ①概念抽取：从文本抽取概念
* ②④概念扩展：根据概念和外部知识(如百科)，获取更多文本语料
* ③实体链接：从文本获取已有知识库中的实体
* ⑤交叉验证：将多个环节中的概念获取方法进行交叉验证，提高获取效果

* (补充)词袋生成：通过补充概念的上下文词，提供概念的更丰富信息
* (补充)利用搜索引擎的概念判别：根据概念在搜索引擎中返回的结果，进一步判别概念是否属于目标领域

使用本项目时，可以根据实际需要，选取流程中的一个或多个工具进行概念获取。

------

This project is maintained by Knowledge Engineering Group of Tsinghua University(THUKEG), and is used for building a scientific concept set of a certain domain. To acquire high-quality, large-scale concept set, we design a pipeline which employs *Concept Extraction*,  *Entity Linking*, *Concept Extraction* and *Cross Valiation* to get concepts from corpus.

The framework of our Concept Acquisition is shown below, including:

* ①**Concept Extraction**: Given texts, obtain concepts.
* ②④**Concept Expansion**: Given several seed concepts and external knowledge (e.g. Wikipedia or Baidubaike), get more texts.
* ③**Entity Linking**: Given texts, discover the entities of the existing knowledge graph(here we emply Xlore).
* ⑤**Cross Validation**: Multiple methods are cross validated to improve the acquisition performance.
* (Ex.)**Word Bag Generation**: Provide more information about concepts by generating its contextual words.
* (Ex.)**Concept Classification**: Further classify whether a concept belongs to the target domain using snippets from Search Engines.

![N7rBB8.png](https://s1.ax1x.com/2020/07/01/N7rBB8.png)

## 环境要求/Enviroment Requirement

Python >= 3.5, Tensorflow >= 1.10

## 预备工作/Before running the code
1. run `bash init.sh`.
2. `cd bert_start/`
3. run `bert_start.sh -l en|zh` to start the BERT service.

## ① 概念抽取/Concept Extraction 

### Format of input files
- **context_file:** unstractured natural language context. 
- **seeds:** Each single line contains an unique concept.

`给个例子哈`

### Format of output file
- **extraction result:** Each single line contains a json-format text with "name"(name of the concept) and "score"(confidence score of relation with seeds)
```
{"name": "强连通图", "score": 0.8718439936637878}
```

### 使用/Usage
The following settings can be modified in `config.py`:
```
result_path = 'processed_data/propagation_results/result.json'
input_text = 'input_data/context/baike_context'
input_seed = 'input_data/seeds/seed_concepts'
```
Then excute the following command:
```
python concifdence_propagation.py -l zh -task extract
```
None: Extract Chinese concepts need setting language as 'zh', while English 'en'.

### 效果/Evaluation

The evaluation is conducted on an running example of "Data Structure & Algorithms", we record our annotation results for evaluation, and the results are listed below.  Sum of high-quality concepts: **XXX**.

```
python evaluation.py --config
```

| algorithm        | mAP@100 | mAP@200 | p@100 | p@200 |
| ---------------- | ------- | ------- | ----- | ----- |
| average_distance | 0.079   | 0.083   | 0.280 | 0.295 |
| graph_prop       | 0.038   | 0.027   | 0.160 | 0.135 |
| pagerank         | 0.010   | 0.018   | 0.130 | 0.155 |
| tf_idf           | 0.115   | 0.095   | 0.300 | 0.285 |

You can edit the output file before next step, to get a better final result.



## ②④ 概念扩展/Concept Expansion

This process is used for searching for more related concepts or texts to expand the concept set.

### Format of input files

- **concepts:** a concept list of target domain

### Format of output file

- **expanded concept list:** More candidate concepts, and each concept is combined with an external web page text.

### Usage

This part need developer to crawl from corresponding external knowledge. Currently we do not provide tool of this part. But a typical solution is to link the concept list at ① step to an external knowledge base, and take the entities that have relationships with these concepts as expanded concept list.

### Evaluation

In our practice, we employ **Baidubaike** as the external knowledge, the example of our expanded result is in the file of XX. 

From 535 concepts provided by step ①, we use the hyperlink of Baidubaike to get more concepts. Finally, we get texts for xxxx concepts in first expansion stage, and texts for xxx concepts based on 2nd-round expansion.



## ③ 实体链接/Entity linking

Entity linking is a supplement method of concept extraction, here we employ Xlink.

Xlink extract concepts that contained in Wikipedia or Baidu Baike from the given context, without knowning seeds. This toolkit ranks concept list according to the frequency of concept's occurrence in the full context. 

### Format of input files
- **context_file:** unstractured natural language context. (usually crawled from Baike web page of seeds)

### Format of output file
- **extraction result:** Each single line contains a json-format text with "name"(name of the concept) and "freq"(frequency of that concept in the input context)
```
{"name": "动态规划", "freq": 68}
```


### Usage: 
The following settings can be modified in `config.py`:

```
lang = "zh" 
# "zh" for extract Chinese concepts, "en" for English.
folder_path = "input_data/context"
file_name = "baike_context"
save_folder = "processed_data/xlink_results"
```
Then excute:
```
python xlink.py
```
### Evaluation

```
python evaluation.py --config
```

The evaluation of Entity Linking is also conducted on "Data Structure and Algorithm". After this step, we get xxx concepts from xxx web pages.

| algorithm        | mAP@100 | mAP@200 | p@100 | p@200 |
| ---------------- | ------- | ------- | ----- | ----- |
| xlink            | 0.428   | 0.338   | 0.620 | 0.525 |


## ⑤ 交叉验证/Cross Validation

This part includes two subsections

	* 5.1 Rerank the concepts Based on Concept Extraction and Entity Linking
	* 5.2 Rerank the concepts Based on Clustering

## 通过概念抽取和实体链接重新评估候选概念/Rerank the concepts Based on Concept Extraction and Entity Linking

Confidence propagation method ranks concepts according to their relation with seeds, while entity linking method could check whether a word should be identified as a concept. This algorithm rerank the concept list based on the results of the two steps above.

Metric: R = log(freq) * max(score-a, 0)
### Format of input files
- **confidence propagation result:** Each single line contains a json-format text with "name"(name of the concept) and "score"(confidence score of relation with seeds)
```
{"name": "强连通图", "score": 0.8718439936637878}
```
- **entity link result:** Each single line contains a json-format text with "name"(name of the concept) and "freq"(frequency of that concept in the input context)
```
{"name": "动态规划", "freq": 68}
```
### Format of output files
- **entity link result:** Each single line contains a json-format text with "name"(name of the concept),  "freq"(frequency of that concept in the input context), "score"(confidence score of relation with seeds), and "R"(value of the metric)
```
{"name": "数组", "freq": 572, "score": 0.8489068150520325, "R": 5.389827359494898}
```
### Usage
The following settings can be modified in `config.py`:

```
result_path = 'processed_data/propagation_results/result.json'
save_folder = "processed_data/xlink_results"
rerank_result_path = "processed_data/rerank_results/rerank_result.json"
```
Then excute:
```
python rerank.py
```
### Evaluation

Ranking results and evaluation (To be designed by Yuquan).

## 通过聚类方法重新评估候选概念/Rerank of expanded concept based on Clustering

Clusters annotation cost less human workload than concepts annotation. This tool use k-means method with cosine distance to cluster word vectors of expanded concepts.

### Format of input files
- **seeds:** Each single line contains an unique concept.
- **entity link result:** Each single line contains a json-format text with "name"(name of the concept),  "freq"(frequency of that concept in the input context), "score"(confidence score of relation with seeds), and "R"(value of the metric)
```
{"name": "数组", "freq": 572, "score": 0.8489068150520325, "R": 5.389827359494898}
```
### Format of output files
- **clustering result:** Each single line contains a json-format text with "name"(name of the concept),  "freq"(frequency of that concept in the input context), "score"(confidence score of relation with seeds), "R"(value of the metric), "cluster"
```
{"name": "选择排序", "freq": 53, "score": 0.8094679713249207, "R": 3.2138241408307735, "cluster": 1}
```
### Usage
 ```
num_clusters = 100 # number of clusters for all expanded concepts
num_seed_clusters = 10 # number of clusters for seeds
wordvector_path = "word_clustering/word_vectors/sgns.baidubaike.bigram-char"
cluster_concept_path = "processed_data/rerank_results/rerank_result.json"
input_seed = 'input_data/seeds/seed_concepts'

cluster_save_path = "processed_data/cluster_results/cluster_result.json"
 ```
Then excute:
```
python clustering.py
```

### Evaluation

Ranking results and evaluation (To be designed by Yuquan).

## 补充：词袋生成工具/EX: Word bag generation

### Format of output files
- **word bag result:** 
*"posi"* for occurrence list of the concept.
*"pre"* for concepts occur before the concept.
*"save"* for concepts occur at the same position.
*"post"* for concepts occur after the concept.

```
{"name": "选择排序", "freq": 53, "score": 0.8094679713249207, "R": 3.2138241408307735, "cluster": 1, "posi": [3, 10,...], "pre":{"列": 10, "地址": 8...}, "same":{"选择": 2}, "post":{ "查找": 4, "复杂度": 2...}}
```

### Usage
```
input_text = 'input_data/context/baike_context'
cluster_save_path = "processed_data/cluster_results/cluster_result.json"
prun_length = 1000
bag_length = 20
save_word_bag = 'processed_data/word_bag_results/word_bag.json'
```
Then excute:
```
python word_bag.py
```

## 补充：概念判别(基于搜索引擎)/EX: Concept Classification(Snippet)

### Format of output files

### Format of output files

- Usage

```
input_text = 
```

Then excute:

```
python xxx.py
```



## 参考文献/Reference

If you employ our tools or some of them for research, please cite the papers listed below.

Course Concept Extraction in Embedding-Based Graph Propagation, IJCNLP2017

```latex
@inproceedings{pan2017course,
  title={Course concept extraction in moocs via embedding-based graph propagation},
  author={Pan, Liangming and Wang, Xiaochen and Li, Chengjiang and Li, Juanzi and Tang, Jie},
  booktitle={Proceedings of the Eighth International Joint Conference on Natural Language Processing (Volume 1: Long Papers)},
  pages={875--884},
  year={2017}
}
```

Course Concept Expansion in MOOCs with External Knowledge and Interactive Game, ACL2019

```
@inproceedings{yu2019course,
  title={Course Concept Expansion in MOOCs with External Knowledge and Interactive Game},
  author={Yu, Jifan and Wang, Chenyu and Luo, Gan and Hou, Lei and Li, Juanzi and Liu, Zhiyuan and Tang, Jie},
  booktitle={Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics},
  pages={4292--4302},
  year={2019}
}
```

XLink: Domain Specific Entity Linking System, JIST19 (In Press)

