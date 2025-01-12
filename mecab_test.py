#!/usr/bin/python3
import sys
import MeCab
mecab = MeCab.Tagger('-r /dev/null -d /opt/homebrew/lib/mecab/dic/ipadic')

if __name__ == "__main__":
    args = sys.argv
    input = args[1]

    mecab_results = mecab.parse(input)
    results = mecab_results.split('\n')
   
    for line in results:
        print(line)