import sys
import subprocess
import os
import platform

config_file_path = os.path.join(os.path.expanduser("~"), ".reposconfg")


# 获取命令执行的结果
def run_cmd(cmd):
    subprocess_result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    subprocess_return = subprocess_result.stdout.read()
    return subprocess_return.decode('utf-8')


def grep_command_str():
    if is_unix_platform():
        return "grep"
    return "findStr"


def is_unix_platform():
    return platform.system() not in "Windows"


def command_prefix():
    prefix = ''
    if is_unix_platform():
        prefix = './'
    return prefix


def print_error(msg, needExit=True):
    msg = f"""
=====================================================

Error: {msg}

=====================================================
"""
    print(msg)
    if needExit:
        sys.exit(-1)
