import argparse
import json
import re
import glob
import os
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='path', action='store', default=f"{os.getcwd()}/logs/",
                    help='Path to logs')
args = parser.parse_args()

dict_ip = defaultdict(
    lambda: {"COUNT": 0, "GET": 0, "POST": 0, "HEAD": 0, "PUT": 0, "OPTIONS": 0, "DELETE": 0}
)

dict_time = defaultdict(
    lambda: {"METHOD": '', "URL": '', "DURATION": 0, "TIME": ''}
)

dict_count = {"TOTAL REQUESTS": 0, "GET": 0, "POST": 0, "HEAD": 0, "PUT": 0, "OPTIONS": 0, "DELETE": 0}


def logs_analyzing(filename):
    with open(filename, 'r') as file:
        for line in file.readlines():
            ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            method_match = re.search(r"GET|POST|HEAD|PUT|OPTIONS|DELETE", line)
            if ip_match is not None and method_match is not None:
                dict_count["TOTAL REQUESTS"] += 1
                dict_count[method_match.group()] += 1

            url_match = re.search(r"http.+(?=\"\s\")|\"-\"", line)
            duration_match = re.search(r"\d+(?=\n)", line)
            time_match = re.search(r"(?<=\[).+(?= \+\d)", line)
            ip = ip_match.group()
            if (method_match is not None) and (ip_match is not None) and \
                    (duration_match is not None) and (time_match is not None) and (url_match is not None):
                if ip in dict_time.keys():
                    if int(duration_match.group()) > dict_time[ip]["DURATION"]:
                        dict_time[ip]["METHOD"] = method_match.group()
                        dict_time[ip]["URL"] = url_match.group()
                        dict_time[ip]["DURATION"] = int(duration_match.group())
                        dict_time[ip]["TIME"] = time_match.group()
                else:
                    dict_time[ip]["METHOD"] = method_match.group()
                    dict_time[ip]["URL"] = url_match.group()
                    dict_time[ip]["DURATION"] = int(duration_match.group())
                    dict_time[ip]["TIME"] = time_match.group()

            if ip_match is not None:
                ip = ip_match.group()
                if method_match is not None:
                    dict_ip[ip][method_match.group()] += 1
                    dict_ip[ip]["COUNT"] += 1

    temp_count_requests = dict_count.copy()
    for key in dict_count.keys(): dict_count[key] = 0
    result = [temp_count_requests]

    temp_dict_ip = dict_ip.copy()
    dict_ip.clear()
    top_frequency_request = dict(sorted(temp_dict_ip.items(), key=lambda x: x[1].get('COUNT'), reverse=True)[:3])
    result.append(top_frequency_request)

    temp_dict_time = dict_time.copy()
    dict_time.clear()

    top_long_request = dict(sorted(temp_dict_time.items(), key=lambda x: x[1].get("DURATION"), reverse=True)[:3])
    result.append(top_long_request)

    return result


if os.path.isfile(args.path):
    filepath = args.path
    result = logs_analyzing(filepath)

    with open(filepath.split('\\')[-1].replace(".", "_") + ".json", "w") as jsonfile:
        json.dump(result, jsonfile, indent=4)
        print(json.dumps(result, indent=4))

elif os.path.isfile(args.path) == False:
    for filepath in glob.glob(f'{args.path}' + '*.log'):
        result = logs_analyzing(filepath)

        with open(filepath.split('\\')[-1].replace(".", "_") + ".json", "w") as jsonfile:
            json.dump(result, jsonfile, indent=4)
            print(json.dumps(result, indent=4))
