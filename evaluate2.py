import os
import dbm as gdbm

def calc_f_measure(right_count, right_file_list,count):
    recoll = right_count / len(right_file_list)
    prec = right_count / count
    f_measure = 2 * recoll * prec / (recoll + prec)
    print(f"Prec:{prec} Recoll:{recoll} F-measure:{f_measure}")
    

if __name__ == "__main__":
    result_txt = open('result2.txt','r')
    eva_txt = open('eva.txt','r')

    right_file_list = []
    result_file_list = []
    count = 1
    right_count = 0

    title_db = gdbm.open('title','r')

    for result_line in result_txt:
        result_line= result_line.rstrip()
        result_file_path = result_line.split(' ')[0]
        file_basename = os.path.basename(result_file_path)
        result_file_list.append(file_basename)
        for eva_line in eva_txt:
            eva_line = eva_line.rstrip()
            eva_value = eva_line.split(' ')[0]
            eva_file = eva_line.split(' ')[1]
            if eva_value == '1':
                right_file_list.append(eva_file)
        if file_basename  in right_file_list:
            right_count += 1
        else:
            title = title_db[file_basename].decode('utf-8')
            print(f"[err] {file_basename} {title}")
        count += 1
    
    for right_file in right_file_list:
        if right_file not in result_file_list:
            title = title_db[right_file].decode('utf-8')
            print(f"[miss] {right_file} {title}")


    # 最後に評価を出力
    calc_f_measure(right_count,right_file_list,count)

    title_db.close()