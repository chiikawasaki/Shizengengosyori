#!/usr/bin/python3
import glob
import os
import sys
  
            
if __name__ == "__main__":
    args = sys.argv
    # 検索キーワードを取得
    keyword = args[1]

    # 転置インデックスを読み込む
    index_file = open('index.txt','r')
    index_hash = {}
    # indecx_hashに格納
    for line in index_file:
        # 改行を除去
        line = line.rstrip()
        line = line.split(' ')
        # 名詞をキー、記事名と出現回数を値とする辞書型オブジェクト
        index_hash.setdefault(line[0],line[1])
    
    # 検索キーワードが含まれる記事を検索
    for key in index_hash:
        if keyword == key:
            file_list = index_hash[key].split(',')
            for file in file_list:
                print(file)