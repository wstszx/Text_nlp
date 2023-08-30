import nltk
from nltk.corpus import movie_reviews
import random

# 获取电影评论数据集
nltk.download('movie_reviews')
documents = [(list(movie_reviews.words(fileid)), category)
             for category in movie_reviews.categories()
             for fileid in movie_reviews.fileids(category)]

# 将数据集分为训练集和测试集
random.shuffle(documents)
train_set = documents[:1600]
test_set = documents[1600:]

# 提取特征
all_words = nltk.FreqDist(w.lower() for w in movie_reviews.words())
word_features = list(all_words)[:2000]

def document_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains({})'.format(word)] = (word in document_words)
    return features

# 训练分类器
train_features = [(document_features(d), c) for (d,c) in train_set]
classifier = nltk.NaiveBayesClassifier.train(train_features)

# 测试分类器
test_features = [(document_features(d), c) for (d,c) in test_set]
print(nltk.classify.accuracy(classifier, test_features))