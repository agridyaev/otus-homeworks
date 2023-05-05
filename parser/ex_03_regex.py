import re
import os
import time

from subprocess import run, PIPE
from collections import defaultdict

run_command = run(["ps", "aux"], stdout=PIPE, check=True)
capture_stdout = run_command.stdout
decode_stdout = capture_stdout.decode('utf-8')
line_by_line = decode_stdout.splitlines()

users_proc = defaultdict(int)
ps_aux_analysis = defaultdict(int)
cpu_mem_process = []
for line in line_by_line[1:]:
    # USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    # root           1  0.0  0.2 168924 13092 ?        Ss   лют16   0:08 /sbin/init splash
    process_parse = re.search(r"^(\S+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s.+\d+:\d+\s(.+)$",
                              line)
    if process_parse is not None:
        dict_cpu_mem = {}

        user = process_parse.group(1)
        cpu = float(process_parse.group(3))
        mem = float(process_parse.group(4))
        name = process_parse.group(5)

        users_proc[user] += 1
        ps_aux_analysis["processes"] += 1
        ps_aux_analysis["cpu"] += cpu
        ps_aux_analysis["mem"] += mem

        dict_cpu_mem["cpu"] = cpu
        dict_cpu_mem["mem"] = mem
        dict_cpu_mem["name"] = name
        cpu_mem_process.append(dict_cpu_mem)

sort_cpu = sorted(cpu_mem_process, key=lambda k: k["cpu"], reverse=True)
sort_mem = sorted(cpu_mem_process, key=lambda k: k["mem"], reverse=True)

text_result = "Отчёт о состоянии системы:\r\n" \
              f"Пользователи системы: {', '.join(users_proc.keys())}\r\n" \
              f"Процессов запущено: {ps_aux_analysis['processes']}\r\n" \
              "Пользовательских процессов:\r\n" \
              f"{os.linesep.join(k + ': ' + str(v) for (k, v) in users_proc.items())}\r\n" \
              f"Всего памяти используется: {ps_aux_analysis['mem']:.1f}%\r\n" \
              f"Всего CPU используется: {ps_aux_analysis['cpu']:.1f}%\r\n" \
              f"Больше всего памяти использует: {sort_mem[0]['name'][:20]}\r\n" \
              f"Больше всего CPU использует: {sort_cpu[0]['name'][:20]}"

print(text_result)
with open(f"{time.strftime('%d-%b-%Y %H:%M:%S', time.localtime())}--scan.txt",
          mode="w", encoding='UTF-8') as result_file:
    result_file.write(text_result)
