import sys
import os
import math
from gensim.models import word2vec
import dbm as gdbm


model = word2vec.Word2Vec.load("model/w2vec.model")
N = 129347 # 全記事数
# テキストを辞書型に変換
def parse_data(lines, delimiter='\t', min_length=2):
    result = {}
    for line in lines:
        line = line.rstrip().split(delimiter)
        if len(line) >= min_length:
            result[line[0]] = line[1]
    return result


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

posdata = open('posdata.txt','r')
dfdata = open('df.txt','r')
noun_tf_hash = parse_data(posdata," ")
noun_df_hash = parse_data(dfdata,"\t")
def create_vector(file):

    object_vector = {}
    
    file_name = os.path.basename(file)
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

def document_vector(noun_tfidf_vec):
    sum_vec = [0] * 300
    word_count = 0
    for noun in noun_tfidf_vec.keys():
        try:
            vec = model.wv[noun] #300次元のベクトル？
        except KeyError:
            continue
        weight_vec = []
        for v in vec:
            weight_vec.append(v * noun_tfidf_vec[noun])
        for i in range(len(sum_vec)):
            sum_vec[i] += weight_vec[i]
        word_count += 1
    if word_count > 0:
        ave_vec = []
        for s_v in sum_vec:
            ave_vec.append(s_v/word_count)
        return ave_vec
    else:
        ave_vec = [0]*300
        return ave_vec



#類似度を計算
def calc_cosin(object_vector,result_vector):
    # 分子の計算
    numerator = 0
    for i in range(len(object_vector)):
        numerator += object_vector[i] * result_vector[i]

    # 分母の計算
    object_denominator = 0
    for o_v in object_vector:
        object_denominator += o_v * o_v 
    object_denominator = math.sqrt(object_denominator)
    result_denominator = 0
    for r_v in result_vector:
        result_denominator += r_v * r_v
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

   try:
       q_vec = model.wv[query]
   except KeyError:
       print("key error")
       return
   
   # 類似の単語
   results = model.wv.most_similar([q_vec],[],10)

   object_vector = {}
   for word,sim in results:
       object_vector[word] = sim
   
   # 単語ベクトルの各要素を含む記事集合
   search_result = search_article(object_vector)
   score_hash = {}   
   for file in search_result:       
       # 単語ベクトルの生成（ hash{名詞} = tfidf値 ）
       result_vector = create_vector(file)
       # 文書の分散表現
       # 文書をベクトルで表す
       d_vec = document_vector(result_vector)       
       # 記事間類似度の計算
       cos = calc_cosin(q_vec,d_vec)       
       if cos > 0.5:
           score_hash[file] = cos  

   sorted_list = sorted(score_hash.items(), key=lambda x:x[1], reverse=True)
   # 類似度の高い記事を出力
   count = 1
   for file_path,cos in sorted_list:
        file_basename = os.path.basename(file_path)
        title_db = gdbm.open('title','r')
        title = title_db[file_basename].decode('utf-8')
        print(count,file_path,cos)
        print(f"-> {title}")
        count += 1
   title_db.close()
   
if __name__ == "__main__":
    main()