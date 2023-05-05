import argparse
import json
import os
import subprocess
from collections import Counter, OrderedDict
from datetime import datetime


class LogReader:
    def __init__(self, parse_args):
        self.counter = 0
        self.REQUEST_COUNTER = {}
        self.IP_LIST = []
        self.LONG_REQUEST = {}
        self.ALL_REQUESTS = None
        self.parse_args = parse_args
        self.file_path = ""
        self.log_name = ""
        self.file_name = ""

    def dir_checker(self):
        if os.path.isdir(self.parse_args.path):
            FILE_DIR = parser_args.path
            FILE_EXE = r".log"
            self.file_path = [_ for _ in os.listdir(FILE_DIR) if _.endswith(FILE_EXE)]
            self.file_path.reverse()
        else:
            log_name = os.path.basename(self.parse_args.path)
            self.log_name = log_name.split(".")[0]
            self.name_file_result()
            self.file_path = self.parse_args.path

    def name_file_result(self):
        self.file_name = self.log_name + "-" + str(self.counter) + "_" + datetime.now().strftime('%d-%m-%Y-%H:%M.json')

    def run_file(self):
        if isinstance(self.file_path, str):
            self.runner()
        else:
            for file_name in self.file_path:
                self.log_name = file_name.split(".")[0]
                self.counter += 1
                self.log_name = self.log_name
                self.file_path = self.parse_args.path + file_name
                self.name_file_result()
                self.runner()

    def runner(self):
        self.request_counter()
        self.read_log_file()
        self.head_request_counter()
        ip = self.most_common_ip_counter()
        long_request = self.long_request()
        self.create_report(ip_address_list=ip, long_request=long_request)

    def request_counter(self):
        res = subprocess.run([f"wc -l < {self.file_path}"], shell=True, capture_output=True)
        ALL_REQUESTS = res.stdout.decode('utf-8').strip("\n")
        return ALL_REQUESTS

    def read_log_file(self):
        with open(f"{self.file_path}") as f:
            if self.IP_LIST is not []:
                self.IP_LIST = []
            res = subprocess.run([f"wc -l < {self.file_path}"], shell=True, capture_output=True)
            self.ALL_REQUESTS = res.stdout.decode('utf-8').strip("\n")

            for _ in f:
                data = f.readline()
                if not data:
                    break
                else:
                    ip_list = data.split()[0]
                    self.IP_LIST.append(ip_list)
                    long_req_key = data.split()[-1]
                    self.LONG_REQUEST[data] = long_req_key

    def head_request_counter(self):
        for request in ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]:
            command = f"grep -c '\"{request}' {self.file_path}"
            res = subprocess.run([command], shell=True, capture_output=True)

            value = res.stdout.decode('utf-8').strip("\n")
            key = request.strip(" /")
            self.REQUEST_COUNTER.update({key: value})

    def most_common_ip_counter(self):
        common = Counter(self.IP_LIST).most_common(3)
        ip_address_list = []
        for i in common:
            ip_address_list.append(i[0])
        return ip_address_list

    def long_request(self):
        item = OrderedDict(sorted(self.LONG_REQUEST.items(), key=lambda x: int(x[1])))
        long_request = list(item)[-3:]
        return long_request

    def create_report(self, ip_address_list, long_request):
        all_dict = {'Отчёт':
            [{
                'Общее количество выполненных запросов': f"{self.ALL_REQUESTS}",
                'Количество запросов по HTTP-методам': f"{self.REQUEST_COUNTER}",
                'Топ 3 IP адресов': f"{ip_address_list}",
                'Топ 3 самых долгих запросов': f"{long_request}",
            }]
        }

        with open(self.file_name, 'w', encoding="utf-8") as file:
            json.dump(all_dict, file, ensure_ascii=False, indent=4)

        print(all_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process access.log')
    parser.add_argument("-path", default=".")
    parser_args = parser.parse_args()
    log = LogReader(parser_args)
    log.dir_checker()
    log.run_file()
