#!/usr/bin/python3
# 作成したデータベースを参照するプログラム

import dbm as gdbm
import sys
import dbm.ndbm


def main():    
    args = sys.argv
    db_file = args[1]
    key = args[2]

    # open the database
    db = dbm.ndbm.open(db_file, 'r')
    
    # 対応するキー（key）に対応する値を取得し、valueに格納．UTF-8文字コードにデコードする必要がある．
    value = db[key].decode('utf-8')
    print(value)
    
    db.close()

if __name__ == "__main__":
    main()