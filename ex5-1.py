#!/usr/bin/python3
import sys
import MeCab
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

if __name__ == "__main__":
    args = sys.argv
    file_path = args[1]

    sentences = extractSentences(file_path)
    for sentence in sentences:
        print(sentence)
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
                    print(sentence_info[0])