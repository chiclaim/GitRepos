import signal
import sys
import os
import getopt
from enum import Enum
from xml.etree import ElementTree as eTree

MANIFEST_NAME = "repo_manifest.xml"


class Manifest:
    branch = ''
    projects = {}


class PrintColor:
    WHITE = '\033[97m'
    # 蓝绿色
    CYAN = '\033[96m'
    # 品红
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Command(Enum):
    PULL = 'pull'
    PUSH = 'push'
    BRANCH = 'branch'
    CHECKOUT = 'checkout'
    STATUS = 'status'


manifest = Manifest()


# 输出带有颜色的日志
def print_with_color(msg, *print_colors):
    pc = ''.join(print_colors)
    print('{0}{1}{2}'.format(pc, msg, PrintColor.END), flush=True)


def check_none(element, err_msg):
    if element is None:
        print_with_color(err_msg, PrintColor.RED)
        sys.exit(-1)


def check_empty(value, err_msg):
    if not value.strip():
        print_with_color(err_msg, PrintColor.RED)
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
            print_with_color("{0} 文件格式有误".format(MANIFEST_NAME), PrintColor.RED)
            sys.exit(-1)


# 解析 Manifest 文件
def parse_manifest():
    element_tree = manifest_tree()
    root = element_tree.getroot()

    config = root.find('config')
    check_none(config, 'config 子节点未找到')

    manifest.branch = config.get('branch')
    check_none(manifest.branch, 'config 节点 branch 属性未设置')
    check_empty(manifest.branch, 'branch 不能为空')

    project_list = root.findall('project')
    for project in project_list:
        manifest.projects[project.get('name')] = project.get('git')


def pull():
    # 上一级目录
    target_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
    for project_name in manifest.projects.keys():
        git_url = manifest.projects[project_name]
        project_dir = os.path.join(target_path, project_name)
        # 项目文件夹不存在
        if not os.path.exists(project_dir):
            print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
            os.chdir(target_path)
            os.system('git clone -b {0} {1} {2}'.format(manifest.branch, git_url, project_name))
        elif os.path.exists(os.path.join(project_dir, '.git')):
            # git pull
            print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
            os.chdir(project_dir)
            os.system('git {0}'.format(Command.PULL.value))
        else:
            print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
            print_with_color('目标文件夹 {0} 已经存在，并且不为空'.format(project_name), PrintColor.RED)
            sys.exit(-1)


def push():
    pass


def checkout():
    pass


def status():
    # 上一级目录
    target_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        if not os.path.exists(project_dir):
            print_with_color('Project `{0}` is not exist, you may need to sync projects'.format(project_name),
                             PrintColor.RED)
            sys.exit(-1)
        os.chdir(project_dir)
        r = os.popen('git status -s')
        lines = r.read().splitlines(False)
        if len(lines) == 0:
            r2 = os.popen('git status')
            lines2 = r2.read().splitlines(False)
            msg = None
            for line in lines2:
                if line.find('All conflicts fixed but you are still merging') != -1:
                    msg = ('Project {0} need to commit (All conflicts fixed but you are still merging)'.format(project_name))
                if line.find('use "git pull"') != -1:
                    msg = ('Project {0} need to pull'.format(project_name))
                elif line.find('use "git push"') != -1:
                    msg = ('Project {0} need to push'.format(project_name))
                # other situations
            if msg is None:
                print_with_color('Project {0} is clean'.format(project_name), PrintColor.GRAY)
            else:
                print_with_color(msg, PrintColor.GREEN)
            continue
        else:
            print_with_color('Project {0}/'.format(project_name), PrintColor.YELLOW)
        for line in lines:
            status_file = line.rsplit(" ", 1)
            print('     {0}{1}{2} {3}'.format(PrintColor.RED, status_file[0], PrintColor.END, status_file[1]))


def branch():
    # 上一级目录
    target_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
    branch_map = {}
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        if not os.path.exists(project_dir):
            print_with_color('Project `{0}` is not exist, you may need to sync projects'.format(project_name),
                             PrintColor.RED)
            sys.exit(-1)
        os.chdir(project_dir)
        r = os.popen('git branch')
        lines = r.read().splitlines(False)
        for line in lines:
            if line.startswith('*'):
                current_branch = line[2:]
                if current_branch in branch_map:
                    branch_map[current_branch] = branch_map[current_branch] + 1
                else:
                    branch_map[current_branch] = 1

    if len(branch_map) > 0:
        if len(branch_map) == 1:
            print('all projects in branch', end=' ')
            print_with_color(next(iter(branch_map)), PrintColor.GREEN)
        else:
            print_with_color('There are {0} projects:'.format(len(manifest.projects)), PrintColor.YELLOW)
            for name in branch_map:
                print_with_color('   {0} projects in {1}'.format(branch_map[name], name), PrintColor.GREEN)


def execute():
    try:
        options, args = getopt.getopt(sys.argv[1:], "h")
        for arg in args:
            if arg == Command.PULL.value:
                pull()
                break
            elif arg == Command.PUSH.value:
                push()
                break
            elif arg == Command.BRANCH.value:
                branch()
                break
            elif arg == Command.STATUS.value:
                status()
                break
            elif arg == Command.CHECKOUT.value:
                checkout()
                break
    except getopt.GetoptError as err:
        print_with_color(err, PrintColor.RED)
        sys.exit(-1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parse_manifest()
    execute()


if __name__ == '__main__':
    main()
