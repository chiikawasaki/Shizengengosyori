#!/usr/bin/python3
import glob
import os
import sys

def extractSentences(file):
    sentences = []
    file = open(file)
    
    for line in file:
        str = line.rstrip() # 改行を除去
        sentences.append(str)
    del sentences[0:2]
    
    return sentences

def extractTitle(file):
    file = open(file)
    
    for line in file:
        str = line.rstrip() # 改行を除去
        if "<title>" in str:
            title_line_list = str.split(" ")
            title = title_line_list[1]
            return title
            
            


if __name__ == "__main__":
    args = sys.argv
    # 検索キーワードを取得
    keyword = args[1]
    
    home = os.environ['HOME']     # ホームディレクトリの取得
    TextDir = home+"/sizengengo/Corpus/*/*"

    files = glob.glob(TextDir)
    files.sort()
    for file in files:
        sentences = extractSentences(file)
        for sentence in sentences:
            if keyword in sentence:
                title = extractTitle(file)
                print(file+" "+title)    
                # 発見したら出力を行い次の記事へ
                break