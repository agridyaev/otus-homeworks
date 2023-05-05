import json
import subprocess

from datetime import datetime
from collections import Counter, defaultdict

process_dct = defaultdict(dict)
# Не обязательно использовать здесь subprocess.Popen и communicate()
# Можно было воспользоваться subprocess.run()
process = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

# Было бы правильно посчитать количество заголовков и затем использовать его
# для разбиения строк с данными
# process_list = proc.split(maxsplit=len(headers) - 1)
# headers = process.split('\n')[0].split()
for proc in process.split('\n')[1:-1]:
    process_list = proc.split()
    # magic numbers
    pid = int(process_list[1])
    process_dct[pid]["user"] = process_list[0]
    process_dct[pid]["cpu"] = float(process_list[2])
    process_dct[pid]["mem"] = float(process_list[3])
    # Если в имени процесса есть пробел, то такое разбиение приводит к тому,
    # часть имени процесса теряется
    process_dct[pid]["command"] = process_list[10]


# Здесь можно было использовать process_dct.values()
counter_proc_by_name = Counter([value["user"] for _, value in process_dct.items()])
# most_memory_uses = max(process_dct.values(), key=lambda x: x["mem"])
most_memory_uses = max(process_dct.items(), key=lambda x: x[1]["mem"])[1]
# max(process_dct.values(), key=lambda x: x["cpu"])
most_cpu_uses = max(process_dct.items(), key=lambda x: x[1]["cpu"])[1]
filename = datetime.now().strftime('%d-%m-%Y-%H:%M-scan.txt')

with open(filename, 'w', encoding="utf-8") as file:
    result = {
        "System_users": list(counter_proc_by_name),
        "Processes_started": len(process_dct),
        "Users_processes": [{user: count} for user, count in counter_proc_by_name.items()],
        # sum(value['mem'] for value in process_dct.values())
        "Total_memory_used": f"{round(sum(value['mem'] for key, value in process_dct.items()), 2)} %",
        # sum(value['cpu'] for value in process_dct.values())
        "Total_CPU_used": f"{round(sum(value['cpu'] for key, value in process_dct.items()), 2)} %",
        # Почему тут не используются most_memory_uses и most_cpu_uses ?
        "Most_memory_uses": max(process_dct.items(), key=lambda x: x[1]["mem"])[1]["command"][:20],
        "Most_CPU_uses": max(process_dct.items(), key=lambda x: x[1]["cpu"])[1]["command"][:20]
    }
    result_dumps = json.dumps(result, indent=4)
    print(result_dumps)
    file.write(result_dumps)
