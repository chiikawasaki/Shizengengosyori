# テキスト記事データの全ての記事の本文を形態素解析してデータベースに格納するプログラム
# 名詞:頻度,名詞:頻度,名詞:頻度,...

import MeCab
import os
import glob
import dbm as gdbm

mecab = MeCab.Tagger('-r /dev/null -d /opt/homebrew/lib/mecab/dic/ipadic')

# 指定したファイルから文を抽出する関数
def extractSentences(file):
    sentences = []
    file = open(file)
    
    for line in file:
        str = line.rstrip() # 改行を除去
        sentences.append(str)
    del sentences[0:2]
    
    return sentences

# 名詞を抽出する関数
def extract_noun(file_path):
    noun_list = [] # 名詞のリスト
    sentences = extractSentences(file_path)
    for sentence in sentences:
        mecab_results = mecab.parse(sentence)
        results = mecab_results.split('\n')
   
        for line in results:
            if line == 'EOS':
                break
            # tabで区切られた形態素解析結果を取得
            sentence_info = line.split('\t')
            sentence_features = sentence_info[1].split(',')

            for sentence_feature in sentence_features:
                if sentence_feature == '名詞':
                    noun_list.append(sentence_info[0])
    return noun_list


if __name__ == "__main__":
    # テキスト記事のディレクトリ
   home = os.environ['HOME']
   TextDir = home+"/Desktop/自然言語処理/Corpus/*/*"
   # posdataに書き込み
   posdata = open('posdata.txt','w')

   files = glob.glob(TextDir)
   files.sort()
   for file in files:
        noun_hash = {} # 辞書型
        noun_list = extract_noun(file)

        # 頻度をnoun_hashに記録
        for noun in noun_list:
            if noun in noun_hash:
                noun_hash[noun] += 1
            else:
                noun_hash[noun] = 1

        # 初期化
        file_basename = os.path.basename(file)
        for noun in noun_hash:
                noun_frequency = noun_hash[noun]
                noun_set = noun + ':' + str(noun_frequency) + ','
                posdata.write(file_basename + ' ' + noun_set)
        print(file)
   posdata.close()
        