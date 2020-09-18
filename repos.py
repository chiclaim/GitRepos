import signal
import sys
import os
from enum import Enum
from xml.etree import ElementTree as eTree

MANIFEST_NAME = "repo_manifest.xml"


class Manifest:
    branch = ''
    projects = {}


class PrintColor:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    WARNING = '\033[93m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Command(Enum):
    PULL = 'git pull'
    PUSH = 'git push'
    BRANCH = 'git branch'
    CHECKOUT = 'status checkout'
    STATUS = 'git status'


manifest = Manifest()


# 输出带有颜色的日志
def print_with_color(msg, *print_colors):
    pc = ''.join(print_colors)
    print(pc, msg, PrintColor.END, flush=True)


def check_none(element, err_msg):
    if element is None:
        print_with_color(err_msg, PrintColor.FAIL)
        sys.exit(-1)


def check_empty(value, err_msg):
    if not value.strip():
        print_with_color(err_msg, PrintColor.FAIL)
        sys.exit(-1)


# 中断执行
def signal_handler(signal_num, frame):
    sys.exit(signal_num)


def manifest_tree():
    manifest_file_path = os.path.abspath(MANIFEST_NAME)

    if not os.path.exists(manifest_file_path):
        print_with_color("当前文件夹找不到{0}文件".format(MANIFEST_NAME), PrintColor.GREEN)
        sys.exit(-1)
    else:
        try:
            return eTree.parse(manifest_file_path)
        except eTree.ParseError:
            print_with_color("{0} 文件格式有误".format(MANIFEST_NAME), PrintColor.FAIL)
            sys.exit(-1)


# 解析 Manifest 文件
def parse_manifest():
    element_tree = manifest_tree()
    root = element_tree.getroot()

    config = root.find('config')
    check_none(config, 'config 子节点未找到')

    branch = config.get('branch')
    check_none(branch, 'config 节点 branch 属性未设置')
    check_empty(branch, 'branch 不能为空')

    manifest.branch = branch

    project_list = root.findall('project')
    for project in project_list:
        manifest.projects[project.get('name')] = project.get('git')


def execute_cmd(command: Command):
    for key in manifest.projects.keys():
        value = manifest.projects[key]
        target_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
        project_dir = os.path.join(target_path, key)
        # 如果项目不存在，则 git clone
        if command == Command.PULL:
            # 项目文件夹不存在
            if not os.path.exists(project_dir):
                print("不存在" + project_dir)
                os.chdir(target_path)
                os.system('git clone -b {0} {1} {2}'.format(manifest.branch, value, key))
            elif os.path.exists(os.path.join(project_dir, '.git')):
                # git pull
                os.chdir(project_dir)
                os.system(command.value)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parse_manifest()
    execute_cmd(Command.PULL)


if __name__ == '__main__':
    main()
