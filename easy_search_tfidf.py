#!/usr/bin/python3
import os
import sys
import math
import dbm as gdbm
import dbm.ndbm
  
N = 129347 # 全記事数
            
if __name__ == "__main__":
    args = sys.argv
    # 検索キーワードを取得
    keywords = args[1:]

    # 転置インデックスを読み込む
    index_file = open('index_advance2.txt','r')
    index_hash = {}
    # indecx_hashに格納
    for line in index_file:
        # 改行を除去
        line = line.rstrip()
        line = line.split(' ')
        # 名詞をキー、記事名と出現回数を値とする辞書型オブジェクト
        index_hash.setdefault(line[0],line[1])
    
    # 検索キーワードが含まれる記事を検索

    keywords_count = len(keywords)
    file_tfidf_sum_hash = {}
    count_files_hash = {}
    and_file_hash = {}

    for keyword in keywords:
        for key in index_hash:
            if keyword == key:
                file_list = index_hash[key].split(',')
                df = len(file_list)

                # 記事とヒット回数を記録_
                for file in file_list:
                    file_name = file.split(':')[0]
                    tf = float(file.split(':')[1])
                    tfidf = tf*math.log2(N/df)
                    
                    # 両方含まれている記事を格納
                    if count_files_hash.get(file_name) is None:
                        count_files_hash[file_name] = 1
                        file_tfidf_sum_hash[file_name] = tfidf
                    else:
                        count_files_hash[file_name] += 1
                        file_tfidf_sum_hash[file_name] += tfidf

    for file in count_files_hash.keys():
            if count_files_hash[file] == keywords_count:
                and_file_hash[file] = file_tfidf_sum_hash[file]

    # 降順でソート
    sorted_list = sorted(and_file_hash.items(), key=lambda x:x[1], reverse=True)
    for file_path,tfidf in sorted_list:
        file_basename = os.path.basename(file_path)
        title_db = gdbm.open('title','r')
        title = title_db[file_basename].decode('utf-8')
        print(f"{file_path} {title} {tfidf}")
        title_db.close()