import subprocess
from datetime import datetime


def ps_parser(arg):
    text = subprocess.getoutput(f"ps {arg}").split("\n")
    title = text.pop(0).split()
    raw_data = map(lambda x: x.split(None, len(title) - 1), text)
    return [dict(zip(title, process)) for process in raw_data if process]


def get_users(_data):
    result_lst = []
    for _ in _data:
        user = _["USER"]
        if user not in result_lst:
            result_lst.append(user)
    return result_lst


def get_proc_by_users(_data):
    result_dict = {user: 0 for user in get_users(_data)}
    for _ in _data:
        result_dict[_["USER"]] += 1
    result_dict = dict((x, y) for x, y in sorted(result_dict.items(), key=lambda pair: pair[1], reverse=True))
    result_dict = str(result_dict).replace(",", "\n").replace("'", "")[1:-1]
    return result_dict


def get_total(_data, param):
    result = 0
    for _ in _data:
        result += float(_[param])
    return result


def find_high_value_proc(_data, _type):
    result_dict = {}
    for item in _data:
        if not result_dict:
            result_dict = {item["COMMAND"][:20]: item[_type]}
        if float(item[_type]) > float(list(result_dict.values())[0]):
            result_dict = {item["COMMAND"][:20]: item[_type]}
    result_dict = str(result_dict).replace(",", "\n").replace("'", "")[1:-1]
    return result_dict


data = ps_parser("aux")
date = datetime.now().strftime('%d-%d-%Y_%H-%M')
filename = f"{date}-test.txt"

with open(filename, "w")as f:
    f.write("Отчёт о состоянии системы:\n")
    f.write(f"Пользователи системы: {str(get_users(data))[1:-1]}\n")
    f.write(f"Процессов запущено: {len(data)}\n")
    f.write(f"Пользовательских процессов: \n {str(get_proc_by_users(data))}\n")
    f.write(f"Всего RSS памяти используется: {round(get_total(data, 'RSS') / 1024 / 1024, 1)}Gb\n")
    f.write(f"Всего VSZ памяти используется: {round(get_total(data, 'VSZ') / 1024 / 1024, 1)}Gb\n")
    f.write(f"Всего CPU используется: {round(get_total(data, '%CPU'), 1)}%\n")
    f.write(f"Больше всего памяти использует: {find_high_value_proc(data, '%MEM')}%\n")
    f.write(f"Больше всего CPU использует: {find_high_value_proc(data, '%CPU')}%\n")


with open(filename, "r") as f:
    for line in f:
        print(line.replace("\n", ""))
