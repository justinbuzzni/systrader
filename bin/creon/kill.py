import os
import subprocess
from io import StringIO
import pandas as pd

output = subprocess.check_output('WMIC PROCESS get Caption,Commandline,Processid /format:list', shell=True)
# output = output.decode("utf-8").strip()
# output = output.decode("cp949").strip()
output = output.decode("euc-kr").strip()
output = output.replace('\r', '')

for p in output.split('\n\n\n'):
    name = ''
    cmd = ''
    pid = ''
    for line in p.split('\n'):
        k, v = line.split('=', 1)
        if k == 'Caption':
            name = v
        elif k == 'CommandLine':
            cmd = v
        elif k == 'ProcessId':
            pid = v
    if name == 'python.exe' and 'systrader\manage.py runserver' in cmd:
        os.system('wmic process where "processid={pid}" call terminate'.format(pid=pid))