# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 16:45
# 可以自动重启的代码
import os
import sys
from time import sleep


path = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.append(path)


def restart_program():
    try:
        python = sys.executable
        print(python)
        print('三秒后重启')
        sleep(3)
        # loc_path = sys.path[0] + r'\run_mu.py'
        # print(loc_path)
        # for root, dirs, files in os.walk(sys.path[0]):
        #     for file in files:
        #         print(file)
        # print(path)
        print(sys.argv[0])
        os.execl(python, '123', sys.argv[0])
    except Exception as e:
        print(e)


restart_program()
