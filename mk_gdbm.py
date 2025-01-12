#!/usr/bin/python3
# テキスト記事データのファイル名に対するタイトルを格納するデータベースを作成するプログラム。


import glob
import os

import dbm as gdbm
import sys

def main():    

    home = os.environ['HOME']
    TextDir = home+"/Desktop/自然言語処理/Corpus/*/*"

    files = glob.glob(TextDir)

    # open the database
    db = gdbm.open('title', 'c')
    
    files.sort()
    for file in files:
        title = extractTitle(file)
        basename = os.path.basename(file)
        
        print(basename+" "+title)
        # データベースに書き込み
        db[basename] = title
        
    db.close()

def extractTitle(file):
    sgml = open(file)
    # lines = sgml.readlines()

    for line in sgml:
        str = line.rstrip()
        e = str.split(" ")
        
        if e[0] == "<title>":
            return e[1]


if __name__ == "__main__":
    main()