#!/usr/bin/env python3  
#coding: utf-8

#基于训练好的词向量模型进行聚类
#聚类采用Kmeans算法
import math
import re
import json
import jieba
import numpy as np
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from collections import defaultdict
import os.path as osp
current_dir = osp.dirname(__file__)
#输入模型文件路径
#加载训练好的模型
def load_word2vec_model(path):
    model = Word2Vec.load(path)
    return model

def load_sentence(path):
    sentences = set()
    with open(path, encoding="utf8") as f:
        for line in f:
            sentence = line.strip()
            sentences.add(" ".join(jieba.cut(sentence)))
    print("获取句子数量：", len(sentences))
    return sentences

#将文本向量化
def sentences_to_vectors(sentences, model):
    vectors = []
    for sentence in sentences:
        words = sentence.split()  #sentence是分好词的，空格分开
        vector = np.zeros(model.vector_size)
        #所有词的向量相加求平均，作为句子向量
        for word in words:
            try:
                vector += model.wv[word]
            except KeyError:
                #部分词在训练中未出现，用全0向量代替
                vector += np.zeros(model.vector_size)
        vectors.append(vector / len(words))
    return np.array(vectors)


def main():
    model = load_word2vec_model(osp.join(current_dir, "model.w2v"))  #加载 #加载词向量模型
    sentences = load_sentence(osp.join(current_dir, "titles.txt"))  #加载所有标题
    vectors = sentences_to_vectors(sentences, model)   #将所有标题向量化

    n_clusters = int(math.sqrt(len(sentences)))  #指定聚类数量
    print("指定聚类数量：", n_clusters)
    kmeans = KMeans(n_clusters)  #定义一个kmeans计算类
    kmeans.fit(vectors)          #进行聚类计算

    sentence_label_dict = defaultdict(list)
    for sentence, label in zip(sentences, kmeans.labels_):  #取出句子和标签
        sentence_label_dict[label].append(sentence)         #同标签的放到一起
    # for label, sentences in sentence_label_dict.items():
    #     print("cluster %s :" % label)
    #     for i in range(min(10, len(sentences))):  #随便打印几个，太多了看不过来
    #         print(sentences[i].replace(" ", ""))
    #     print("---------")
    
    # 实现基于kmeans的类内距离计算筛选优质类别
    # 1. 计算每个类别的中心点
    center_vectors = kmeans.cluster_centers_
    # 2. 计算每个cluster内的平均距离
    cluster_avg_distance_dict = defaultdict(float)
    for i in range(n_clusters):
        cluster_vectors = vectors[kmeans.labels_ == i]
        cluster_center = center_vectors[i]
        avg_distance = np.mean(np.linalg.norm(cluster_vectors - cluster_center, axis=1))
        cluster_avg_distance_dict[i] = avg_distance
        
    # 3. 选取距离最小的前n个类别并打印
    n = 5
    cluster_avg_distance_dict = dict(sorted(cluster_avg_distance_dict.items(), key=lambda x: x[1]))
    for label, distance in list(cluster_avg_distance_dict.items())[:n]:
        print("cluster %s :" % label)
        print("average distance: ", distance)
        for i in range(min(100, len(sentence_label_dict[label]))):
            print(sentence_label_dict[label][i].replace(" ", ""))
        print("---------")
    # 4. 打印最后n个类别
    for label, distance in list(cluster_avg_distance_dict.items())[-n:]:
        print("cluster %s :" % label)
        print("average distance: ", distance)
        for i in range(min(100, len(sentence_label_dict[label]))):
            print(sentence_label_dict[label][i].replace(" ", ""))
        print("---------")
    

if __name__ == "__main__":
    main()
