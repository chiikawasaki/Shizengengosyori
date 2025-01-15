import os

def calc_f_measure(right_count, right_file_list,count):
    recoll = right_count / len(right_file_list)
    prec = right_count / count
    f_measure = 2 * recoll * prec / (recoll + prec)
    print(f"{count}  Prec:{prec} Recoll:{recoll} F-measure:{f_measure}")
    

if __name__ == "__main__":
    result_txt = open('result.txt','r')
    eva_txt = open('eva.txt','r')

    right_file_list = []
    count = 1
    right_count = 0

    for result_line in result_txt:
        result_line= result_line.rstrip()
        result_file_path = result_line.split(' ')[0]
        file_basename = os.path.basename(result_file_path)
        for eva_line in eva_txt:
            eva_line = eva_line.rstrip()
            eva_value = eva_line.split(' ')[0]
            eva_file = eva_line.split(' ')[1]
            if eva_value == '1':
                right_file_list.append(eva_file)
        if file_basename in right_file_list:
            right_count += 1
        if count == 5:
            calc_f_measure(right_count,right_file_list,count)
        if count == 10:
            calc_f_measure(right_count,right_file_list,count)
        if count == 20:
            calc_f_measure(right_count,right_file_list,count)
        if count == 50:
            calc_f_measure(right_count,right_file_list,count)
        if count == 80:   
            calc_f_measure(right_count,right_file_list,count)
        count += 1