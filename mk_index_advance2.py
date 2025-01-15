# !/usr/bin/python3

# 転置インデックス生成プログラム
# 検索対象のテキスト記事データにおける転置インデックス（index.db）を生成するプロブラム
import MeCab
import os
import glob
import dbm as gdbm

mecab = MeCab.Tagger('-r /dev/null -d /opt/homebrew/lib/mecab/dic/ipadic')

def extractNGram(text,N):
   strList = text.split(":")
   length = len(strList)
   result = []
   for i in range(length-N):
       ngram = ''.join(strList[i:i+N]) # iからi+N-1まで連結
       result.append(ngram)
   
   return result

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

        noun_ngram = ""
        cn = 0
        for line in results:
            if line == 'EOS':
                break
            # tabで区切られた形態素解析結果を取得
            word = line.split('\t')[0]
            word_info = line.split('\t')[1]
            # 名詞が入っているかもしれない部分を取得
            word_feature = word_info.split(',')[0]
            if  word_feature == '名詞':
                    noun_ngram += word + ":"
                    cn += 1
            else:
                    if cn > 0 and cn < 6:
                        for i in range(cn):
                            ngram_result_list = extractNGram(noun_ngram,i+1)
                            for noun in ngram_result_list:
                                noun_list.append(noun)
                    cn = 0
                    noun_ngram = ""
        # 最後の名詞の処理
        if noun_ngram != "":
            if cn > 0 and cn < 6:
                for i in range(cn):
                    ngram_result_list = extractNGram(noun_ngram,i+1)
                    for noun in ngram_result_list:
                        noun_list.append(noun)
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
        noun_list = get_noun_list(file)
        # noun_list の名詞の重複を除去
        # 辞書型オブジェクトに格納する方法が簡単
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
            # file:単語の出現回数の文字列を作成
            file_tf = "" 
            file_tf = file + ":" + str(noun_hash[word]) 
            index.setdefault(word, []).append(file_tf)
        
    # 既存の転置インデックスを消去
    if os.path.isfile("index_advance2.txt") is True:
        os.remove("index_advance2.txt")
    
    # 転置インデックスの生成
    db = open('index_advance2.txt', 'w')
    for noun, file_list in index.items():
        f_data = ','.join(file_list)
        db.write(f"{noun} {f_data}\n")
    db.close()


if __name__ == "__main__":
    main()
