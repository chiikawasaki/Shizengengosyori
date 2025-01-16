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

index_file = open('index_advance2.txt','r')
index_hash = parse_data(index_file,' ')
def easy_search(keywords):
    result_file_list = []
    keywords_count = len(keywords)
    file_tfidf_sum_hash = {}
    count_files_hash = {}
    and_file_hash = {}

    for keyword in keywords:
        if keyword in index_hash.keys():
                file_list = index_hash[keyword].split(',')
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
    for file,tfidf in sorted_list:
        result_file_list.append(file)
    return result_file_list

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


def calc_similarity_of_cluster(file_list_str1, file_list_str2, similarity_cache):
    min_sim = float('inf')
    file_list1 = file_list_str1.split(" ")
    file_list2 = file_list_str2.split(" ")
    
    for file1 in file_list1:
        for file2 in file_list2:
            # キャッシュキーを生成（順序を考慮せず一意性を保つ）
            cache_key = tuple(sorted([file1, file2]))
            
            if cache_key in similarity_cache:
                # キャッシュがある場合は再計算しない
                sim = similarity_cache[cache_key]
            else:
                # キャッシュがない場合は計算してキャッシュに保存
                file1_vec = create_vector(file1)
                file1_doc_vec = document_vector(file1_vec)
                file2_vec = create_vector(file2)
                file2_doc_vec = document_vector(file2_vec)
                sim = calc_cosin(file1_doc_vec, file2_doc_vec)
                similarity_cache[cache_key] = sim
            
            if sim < min_sim:
                min_sim = sim
    return min_sim


def main():
    args = sys.argv
    keywords = args[1:]

    search_result = easy_search(keywords)
    print(search_result)

    ClasterHash = {}
    id = 1
    claster_size = 0
    for file in search_result:
       g_name = "group"+str(id)
       ClasterHash[g_name] = file
       id+=1
       claster_size += 1
    
    similarity_cache = {}
    while claster_size > 20:
        best_sim = 0
        agg_claster1 = ""
        agg_claster2 = ""
       
        ClasterList = list(ClasterHash.keys())    
        for i in range(0,len(ClasterList)-1):
            g_name1 = ClasterList[i]
            g_list1 = ClasterHash[g_name1]
            print(g_list1)
       
            for j in range(i+1,len(ClasterList)):
                g_name2 = ClasterList[j]
                g_list2 = ClasterHash[g_name2]
                sim = calc_similarity_of_cluster(g_list1,g_list2,similarity_cache)

                if sim > best_sim:
                   best_sim = sim
                   agg_claster1 = g_name1
                   agg_claster2 = g_name2

        g_list1 = ClasterHash[agg_claster1]
        g_list2 = ClasterHash[agg_claster2]
        ClasterHash[agg_claster1] = g_list1+" "+g_list2

        del ClasterHash[agg_claster2]        
        claster_size -= 1

    title_db = gdbm.open('title','r')
    groupcount = 1
    for file_str in ClasterHash.values():
        file_list = file_str.split(' ')
        file_count = 1
        print("\n")
        for file in file_list:
            title = title_db[os.path.basename(file)].decode('utf-8')
            print(f"{file_count} group{groupcount} {file}")
            print(f"->{title}")
            file_count += 1
            if file_count > 5:
                break
        groupcount += 1



if __name__ == "__main__":
    main()