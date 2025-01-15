import MeCab
import os
import glob
import dbm as gdbm
import sys

mecab = MeCab.Tagger('-r /dev/null -d /opt/homebrew/lib/mecab/dic/ipadic')

def extractNGram(text,N):
   strList = text.split(":")
   length = len(strList)
   result = []
   for i in range(length-N):
       ngram = ''.join(strList[i:i+N]) # iからi+N-1まで連結
       result.append(ngram)
   
   return result

if __name__ == "__main__":
    args = sys.argv
    # 検索キーワードを取得
    keyword = args[1]

    mecab_results = mecab.parse(keyword)
    results = mecab_results.split('\n')
    
    
    noun_ngram = ""
    cn = 0
    for result in results:
            if result == 'EOS':
                break
            # tabで区切られた形態素解析結果を取得
            word = result.split('\t')[0]
            word_info = result.split('\t')[1]
            if word_info.split(',')[0] == '名詞':
                    noun_ngram += word +  ":"
                    cn += 1
            else:
                    if cn > 0 and cn < 6:
                        for i in range(cn):
                            ngram_result_list = extractNGram(noun_ngram,i+1)
                            for noun in ngram_result_list:
                                print(noun)
                    cn = 0
                    noun_ngram = ""

    # 最後の名詞の処理
    if noun_ngram != "":
        if cn > 0 and cn < 6:
            for i in range(cn):
                ngram_result_list = extractNGram(noun_ngram,i+1)
                for noun in ngram_result_list:
                    print(noun)

                            