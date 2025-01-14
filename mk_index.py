# !/usr/bin/python3

# 転置インデックス生成プログラム
# 検索対象のテキスト記事データにおける転置インデックス（index.db）を生成するプロブラム
import MeCab
import os
import glob
import dbm as gdbm

mecab = MeCab.Tagger('-r /dev/null -d /opt/homebrew/lib/mecab/dic/ipadic')

def extractSentences(file):
    sentences = []
    file = open(file)
    
    for line in file:
        str = line.rstrip() # 改行を除去
        sentences.append(str)
    del sentences[0:2]
    
    return sentences

def get_noun_list(file):
    noun_list = [] # 名詞のリスト
    sentences = extractSentences(file)
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

def main():
    # 記事のディレクトリ
    home = os.environ['HOME']
    TextDir = home+"/Desktop/自然言語処理/Corpus/*/*"
    
    files = glob.glob(TextDir)
    
    index = {}
    files.sort()
    for file in files:
        print(file) # デバック用
        # file の名詞を出力（本関数を実装せよ）
        noun_list = get_noun_list(file)
        # noun_list の名詞の重複を除去
        # 辞書型オブジェクトに格納する方法が簡単
        #（実装せよ。get_noun_list関数で行ってもよい）
        noun_hash = {}
        # 重複がないようにnoun_hashに格納
        for noun in noun_list:
            if noun_hash.get(noun) is None:
                noun_hash[noun] = 1
            else:
                noun_hash[noun] += 1
        
        # 辞書型オブジェクト index に転置インデックスを格納 
        # キーを名詞、値をファイル列の辞書型オブジェクトを作成
        # index[名詞] = fileの格納されたリスト（文字列の連結だとすごく遅い）
        for word in noun_hash.keys():
            index.setdefault(word, []).append(file)
        
    # 既存の転置インデックスを消去
    if os.path.isfile("index") is True:
        os.remove("index")
    
    # 転置インデックスの生成
    db = open('index.txt', 'w')
    for noun, file_list in index.items():
        f_data = ','.join(file_list)
        db.write(f"{noun} {f_data}\n")
    db.close()


if __name__ == "__main__":
    main()
