import argparse
import json
import os
import re
from collections import defaultdict

parser = argparse.ArgumentParser(description='Process access.log')
parser.add_argument('-p', dest='path', action='store', required=True, help='Path to logfile')
args = parser.parse_args()


def parse_log_file(logs):
    total_requests = 0
    by_method = defaultdict(int)
    by_ip = defaultdict(int)
    ip_duration = []

    with open(logs) as logfile:
        for line in logfile:
            method = re.search(r"]\s\"(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE)", line)
            ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            date = re.search(r"\[\d.*?\]", line)
            url = re.search(r"\s(\S*)\sHTTP", line)
            duration = int(line.split()[-1])
            total_requests += 1

            if ip_match is not None:
                ip = ip_match.group()
                if method is not None:
                    by_method[method.group(1)] += 1
                    by_ip[ip] += 1

                    d_dict = {
                        "IP": ip,
                        "DATE": date.group(),
                        "METHOD": method.group(1),
                        "URL": url.group(1),
                        "DURATION": duration
                    }

                    ip_duration.append(d_dict)

        three_top_ips = dict(sorted(by_ip.items(), key=lambda x: x[1], reverse=True)[:3])
        three_top_longest = sorted(ip_duration, key=lambda x: x["DURATION"], reverse=True)[:3]

        result = {"top_ips": three_top_ips,
                  "top_longest": three_top_longest,
                  "total_stat": by_method,
                  "total_requests": total_requests
                  }

        result_json = json.dumps(result, indent=4)
        print(result_json)

        with open(f"{logs}[result].json", "w", encoding='UTF-8') as f:
            f.write(result_json)


if os.path.isfile(args.path):
    parse_log_file(logs=args.path)
elif os.path.isdir(args.path):
    for file in os.listdir(args.path):
        if file.endswith(".log"):
            path_to_logfile = os.path.join(args.path, file)
            parse_log_file(logs=path_to_logfile)
else:
    print("ERROR: Incorrect path to log file or directory")


