# -*- coding: utf-8 -*-
# @Time    : 2019/1/17 11:25
import os
import sys

path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)

import subprocess
from time import sleep
while True:
    try:

        print('启动')
        subprocess.call('D:\\myGitProject\\pc\\docment_two\\sougou\\sougo_mongo_three.bat')
        sleep(10)
        print('关闭')
        subprocess.call('D:\\myGitProject\\pc\\docment_two\\sougou\\qingxi.bat')
    except Exception as e:
        print(e)

# p = subprocess.Popen("cmd.exe /c" + "D:\\myGitProject\\pc\\docment_two\\sougou\\sougo_mongo_three.bat", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# curline = p.stdout.readline()
# while (curline != b''):
#     print(curline)
#     curline = p.stdout.readline()
#
# p.wait()
# print(p.returncode)