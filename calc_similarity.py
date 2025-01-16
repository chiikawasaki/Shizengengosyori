#!/usr/bin/python3

from gensim.models import word2vec
import sys

def main():

    args = sys.argv
    input_str = args[1]
    
    model = word2vec.Word2Vec.load("model/w2vec.model")

    # 単語のベクトル
    try:
        vec = model.wv[input_str]
    except KeyError:
        print("key error")
        return
    
    # 類似の単語
    results = model.wv.most_similar([vec],[],10)

    for word,sim in results:
        print(word,sim)
    
    
if __name__ == '__main__':
    
    main()
