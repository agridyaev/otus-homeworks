"""
Отчёт о состоянии системы:
Пользователи системы: 'root', 'user1', ...
Процессов запущено: 833

Пользовательских процессов:
root: 533
user1: 231
...

Всего памяти используется: 71.3% (используем данные %MEM)
Всего CPU используется: 33.2% (используем данные %CPU)
Больше всего памяти использует: (%имя процесса, первые 20 символов если оно длиннее)
Больше всего CPU использует: (%имя процесса, первые 20 символов если оно длиннее)
"""
import datetime
import logging
import sys
from collections import defaultdict

from subprocess import (
    PIPE, Popen
)
from typing import Iterator, Callable


def get_info_iterator(info_type=None, source=None) -> Iterator[str]:
    """

    :param source:
    :param info_type: system|file
    :return:
    """
    info_type = info_type or 'system'
    source = source or ["ps", "aux"]

    def cleaner(iterator: Iterator[str]):
        return filter(lambda x: x, iter(line.strip() for line in iterator))

    if info_type == 'system':
        with Popen(source, stderr=PIPE, stdout=PIPE, encoding='utf-8') as p:
            yield from cleaner(p.stdout)

    elif info_type == 'file':
        with open(source) as f:
            yield from cleaner(f)


def get_logger() -> Callable:
    dt = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')
    file_log = logging.FileHandler(dt + '-scan.txt', encoding='utf-8')

    logger = logging.getLogger()
    logger.addHandler(file_log)
    logger.setLevel(logging.INFO)
    file_eol_to_replace = '\r\n' if sys.platform in ('linux', 'linux2') else ''

    def log(s: str):
        logger.info(s)
        s = s.replace('\n', file_eol_to_replace) if file_eol_to_replace else s
        print(s)

    return log


def parse():
    logger = get_logger()
    info_iterator = get_info_iterator()

    head_line = next(info_iterator)
    head = [s.strip() for s in head_line.split(' ') if s]
    ln = len(head) - 1

    mem_ind = head.index('%MEM')
    mem_info = .0

    cpu_ind = head.index('%CPU')
    cpu_info = .0

    command_ind = head.index('COMMAND')

    users = set()
    user_proc_cnt = defaultdict(int)
    proc_cpu_cnt = defaultdict(int)
    proc_mem_cnt = defaultdict(int)

    for line in info_iterator:
        info_list = [ss for ss in line.split(' ') if ss]
        info_list = info_list[:ln] + [' '.join(info_list[ln:])]

        user = info_list[0]
        users.add(user)
        user_proc_cnt[user] += 1

        command = info_list[command_ind]
        mem_info_ = float(info_list[mem_ind])
        cpu_info_ = float(info_list[cpu_ind])

        proc_mem_cnt[command] += mem_info_
        proc_cpu_cnt[command] += cpu_info_

        mem_info += mem_info_
        cpu_info += cpu_info_

    logger('Отчёт о состоянии системы:')
    logger('Пользователи системы: ' + ', '.join(f"'{u}'" for u in user_proc_cnt))
    cnt = sum(l for l in user_proc_cnt.values())
    logger(f'Процессов запущено: {cnt}\n')

    ranked_user_proc_cnt = sorted(user_proc_cnt.items(), key=lambda x: x[1], reverse=True)
    logger('Пользовательских процессов:')
    logger('\n'.join(f'{user}: {cnt}' for user, cnt in ranked_user_proc_cnt) + '\n')

    logger(f'Всего памяти используется: {round(mem_info, 1)}%')
    logger(f'Всего CPU используется: {round(cpu_info, 1)}%')

    p, cnt = list(sorted(proc_mem_cnt.items(), key=lambda x: x[1]))[-1]
    logger(f'Больше всего памяти ({round(cnt, 1)}%) использует: {p[:20]}')
    p, cnt = list(sorted(proc_cpu_cnt.items(), key=lambda x: x[1]))[-1]
    logger(f'Больше всего CPU ({round(cnt, 1)}%) использует: {p[:20]}')


if __name__ == '__main__':
    parse()
