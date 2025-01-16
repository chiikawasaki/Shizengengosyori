import sys
import os
import math
import dbm as gdbm

index_file = open('index_advance2.txt','r')
N = 129347 # 全記事数

# テキストを辞書型に変換
def parse_data(lines, delimiter='\t', min_length=2):
    result = {}
    for line in lines:
        line = line.rstrip().split(delimiter)
        if len(line) >= min_length:
            result[line[0]] = line[1]
    return result

# 上位2記事のリストを返す
def easy_search(keywords):
    top2_article_list =[]
    index_hash = parse_data(index_file," ")
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
    count = 1
    for file_path,tfidf in sorted_list:
        top2_article_list.append(file_path)
        count += 1
        if count > 2:
            break
    return top2_article_list

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
   
   keywords = query.split(" ")
   # 入力されたキーワードで検索を実行
   search_result = easy_search(keywords)

   p_vec = {}
   # 検索結果の上位２文書を適合文書としてベクトル生成（実装せよ）→ p_vec
   for file in search_result:
        vec = create_vector(file)
        for noun in vec.keys():
            if noun not in p_vec.keys():
                p_vec[noun] = vec[noun]
   
   # 単語ベクトルの各要素を含む記事集合
   search_result = search_article(p_vec)

   score_hash = {}   
   for file in search_result:
        # 単語ベクトルの生成（ hash{名詞} = tfidf値 ）
        result_vector = create_vector(file)
        # 記事間類似度の計算
        cos = calc_cosin(p_vec,result_vector)
       
        if cos > 0.3:
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