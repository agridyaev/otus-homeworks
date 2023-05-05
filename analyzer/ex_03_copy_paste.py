import argparse
import re
import json
from collections import defaultdict
import os
import sys
from pathlib import Path
import datetime

dt = datetime.datetime.now()
dt_string = dt.strftime("%H-%M-%S")

parser = argparse.ArgumentParser(description='Process access.log')
parser.add_argument('-f', dest='file', action='store', help='Path to logfile')
args = parser.parse_args()


def parser_log():
    dict_method = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0, "CONNECT": 0, "OPTIONS": 0, "TRACE": 0}
    ip_method = defaultdict(lambda: {})
    general_dict = {
        "top_ips": {},
        "top_longest": [{"ip": "", "date": "", "method": "", "url": "", "duration": 0},
                        {"ip": "", "date": "", "method": "", "url": "", "duration": 0},
                        {"ip": "", "date": "", "method": "", "url": "", "duration": 0}],
        "total_stat": {},
        "total_requests": 0}
    for line in file:
        ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
        if ip_match is not None:
            ip = ip_match.group()
            if ip in ip_method:
                ip_method[ip] += 1
            else:
                ip_method[ip] = 1

        method_match = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD|CONNECT|OPTIONS|TRACE)", line)
        if method_match is not None:
            method = method_match.group(1)
            dict_method[method] += 1

        url = re.search(r"(http)?:\/\/(\S+)", line)
        if url is not None:
            url = url.group(0)[:-1]
        elif url is None:
            url = "-"

        longest = re.search(r"\d+$", line)
        longest = longest.group(0)
        if int(longest) > general_dict["top_longest"][0]["duration"]:
            general_dict["top_longest"][0]["ip"] = ip
            general_dict["top_longest"][0]["date"] = str("[" + re.search(r"\[([^\[\]]+)\]", line).group(1) + "]")
            general_dict["top_longest"][0]["method"] = method
            general_dict["top_longest"][0]["url"] = url
            general_dict["top_longest"][0]["duration"] = int(longest)
        elif int(longest) > general_dict["top_longest"][1]["duration"]:
            general_dict["top_longest"][1]["ip"] = ip
            general_dict["top_longest"][1]["date"] = str("[" + re.search(r"\[([^\[\]]+)\]", line).group(1) + "]")
            general_dict["top_longest"][1]["method"] = method
            general_dict["top_longest"][1]["url"] = url
            general_dict["top_longest"][1]["duration"] = int(longest)
        elif int(longest) > general_dict["top_longest"][2]["duration"]:
            general_dict["top_longest"][2]["ip"] = ip
            general_dict["top_longest"][2]["date"] = str("[" + re.search(r"\[([^\[\]]+)\]", line).group(1) + "]")
            general_dict["top_longest"][2]["method"] = method
            general_dict["top_longest"][2]["url"] = url
            general_dict["top_longest"][2]["duration"] = int(longest)

    ip_method = dict(sorted(ip_method.items(), key=lambda x: x[1], reverse=True))
    total_requests = sum(dict_method.values())
    keys = list(ip_method.keys())

    for i in range(0, 3):
        general_dict["top_ips"][keys[i]] = ip_method[keys[i]]
    general_dict["total_stat"] = dict_method
    general_dict["total_requests"] = total_requests
    return general_dict


if os.path.isfile(args.file):
    if Path(args.file).stat().st_size > 0:
        print("Логи по файлу", args.file)
        with open(args.file) as file:
            path = str(Path.cwd() / f"{args.file + dt_string}.json")
            with open(f'{path}', 'w') as outfile:
                json.dump(parser_log(), outfile)
            with open(f'{path}') as outfile:
                json_data = json.load(outfile)
            print(json.dumps(json_data, indent=4))

    else:
        print(f"Файл '{args.file}' пустрй")


elif os.path.isdir(args.file):
    if len(os.listdir(args.file)) >= 1:
        for filename in os.listdir(args.file):
            path_file = os.path.join(args.file, filename)
            if Path(path_file).stat().st_size > 0:
                print("Логи по файлу", path_file)
                with open(os.path.join(args.file, filename)) as file:
                    path = str(Path.cwd() / f"{path_file + dt_string}.json")
                    with open(f'{path}', 'w') as outfile:
                        json.dump(parser_log(), outfile)
                    with open(f'{path}') as outfile:
                        json_data = json.load(outfile)
                    print(json.dumps(json_data, indent=4))
            else:
                print(f"Файл '{path_file}' пустой")
    else:
        print("Директория пуста")
sys.stdout.close()
