import sys
import os
import math
import dbm as gdbm

N = 129347 # 全記事数
posdata = open('posdata.txt','r')
dfdata = open('df.txt','r')

def parse_data(lines, delimiter='\t', min_length=2):
    result = {}
    for line in lines:
        line = line.rstrip().split(delimiter)
        if len(line) >= min_length:
            result[line[0]] = line[1]
    return result

noun_tf_hash = parse_data(posdata," ")
noun_df_hash = parse_data(dfdata,"\t")
# 入力された記事から記事に関連している単語:tfidf値の辞書型オブジェクトを生成
def create_vector(query):
    object_vector = {}
    
    file_name = os.path.basename(query)
    noun_tf_str = noun_tf_hash[file_name]
    noun_tf_list = noun_tf_str.split(',')

    for noun_tf in noun_tf_list:
        noun = noun_tf.split(':')[0]
        if len(noun_tf.split(':')) >= 2:
            tf = noun_tf.split(':')[1]
        if noun_df_hash.get(noun) is not None:
            df = float(noun_df_hash[noun])
            tfidf = float(tf) * math.log2(N/df)
            if len(noun) >=2 and tfidf >= 20:
                object_vector[noun] = tfidf
    return object_vector

#object_vectorから単語を取り出し、その単語を含む記事を検索
def search_article(object_vector):
    all_file_list = []
    # tfの情報はいらないのでindex_advance.txtを開く
    index_file = open('index_advance.txt','r')
    noun_filelist_hash = parse_data(index_file,' ')
    # or検索を行う
    for noun in object_vector.keys():
        file_list = noun_filelist_hash[noun].split(',')
        for file in file_list:
            if file not in all_file_list:
                all_file_list.append(file)

    return all_file_list

#類似度を計算
def calc_cosin(object_vector,result_vector):
    # 分子の計算
    numerator = 0
    for noun in object_vector.keys():
        # もし対応する名詞があれば
        if result_vector.get(noun) is not None:
            numerator += object_vector[noun] * result_vector[noun]
    # 分母の計算
    object_denominator = 0
    for tfidf in object_vector.values():
        object_denominator += tfidf * tfidf
    object_denominator = math.sqrt(object_denominator)
    result_denominator = 0
    for tfidf in result_vector.values():
        result_denominator += tfidf * tfidf
    result_denominator = math.sqrt(result_denominator)
    # 類似度の計算
    if (object_denominator * result_denominator) == 0:
        cos = 0
    else:
        cos = numerator / (object_denominator * result_denominator)
    return cos    


def main():
   args = sys.argv
   query = args[1]
   # 単語ベクトルの生成（ 辞書型オブジェクト vector[名詞] = tfidf値 ）
   object_vector = create_vector(query)
   # 単語ベクトルの各要素（名詞）を含む記事集合→単語ベクトルの名詞のOR検索
   search_result = search_article(object_vector)
   score_hash = {}
   for file in search_result:
       # 単語ベクトルの生成（ 辞書型オブジェクト vector[名詞] = tfidf値 ）
       result_vector = create_vector(file)
       # 記事間類似度の計算
       cos = calc_cosin(object_vector,result_vector)
       if cos > 0.3:
           score_hash[file] = cos

   sorted_list = sorted(score_hash.items(), key=lambda x:x[1], reverse=True)
   # 類似度の高い記事を出力
   count = 1
   for file_path,cos in sorted_list:
        file_basename = os.path.basename(file_path)
        title_db = gdbm.open('title','r')
        title = title_db[file_basename].decode('utf-8')
        print(count,file_path,title,cos)
        print(f"-> {title}")
        count += 1
   title_db.close()

if __name__ == "__main__":
    main()