from subprocess import run, PIPE

res = run(['ps', 'aux'], stdout=PIPE)
procs = res.stdout.decode().splitlines()
titles = procs[0].split()

max_cpu = 0
max_cpu_proc = ''

for p in procs[1:]:
    chunks = p.split(maxsplit=len(titles) - 1)
    proc_cpu = float(chunks[titles.index('%CPU')])
    if proc_cpu >= max_cpu:
        max_cpu = proc_cpu
        max_cpu_proc = chunks[titles.index('COMMAND')]

print(f'Max CPU usage: {max_cpu} ({max_cpu_proc[:20]})')
