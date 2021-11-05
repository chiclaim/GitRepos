import signal
import sys
import os
import getopt
import string
from enum import Enum
from xml.etree import ElementTree as eTree

MANIFEST_NAME = "repos_manifest.xml"
manifest_dir: string


class Manifest:
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
    MERGE = 'merge'
    CUSTOM = '-c'


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

    project_list = root.findall('project')
    for project in project_list:
        manifest.projects[project.get('name')] = project.get('git')


def check_project_exist(project_dir, project_name):
    if not os.path.exists(project_dir):
        print_with_color('err: project `{0}` is not exist, you may need to sync projects'.format(project_name),
                         PrintColor.RED)
        sys.exit(-1)


# manifest 上一级目录
def get_parent_dir():
    return os.path.dirname(manifest_dir)


# 获取仓库的当前分支
def get_actual_branch(project_dir):
    os.chdir(project_dir)
    r = os.popen('git branch')
    lines = r.read().splitlines(False)
    for line in lines:
        if line.startswith('*'):
            return line[2:]


# 获取 remote, 例如 origin
def get_remote(project_dir):
    os.chdir(project_dir)
    r = os.popen('git remote')
    lines = r.read().splitlines(False)
    return lines[0]


def pull(custom_dir=None, branch_name='master'):
    # 如果用户自定了目录，则使用用户自定义的目录
    target_path = get_parent_dir() if custom_dir is None else custom_dir
    for project_name in manifest.projects.keys():
        git_url = manifest.projects[project_name]
        project_dir = os.path.join(target_path, project_name)
        # 项目文件夹不存在
        if not os.path.exists(project_dir):
            os.chdir(target_path)
            print_with_color('{0:-^80}'.format(project_dir), PrintColor.GREEN)
            os.system('git clone -b {0} {1} {2}'.format(branch_name, git_url, project_name))
        elif os.path.exists(os.path.join(project_dir, '.git')):
            # git pull
            print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
            os.chdir(project_dir)
            os.system('git {0}'.format(Command.PULL.value))
        else:
            print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
            print_with_color('目标文件夹 {0} 已经存在，并且不为空'.format(project_name), PrintColor.RED)
            sys.exit(-1)
        # 文件夹存在，但是 .git 文件夹为空


def push(has_option=False):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        print_with_color('{0:-^50}'.format(project_name), PrintColor.GREEN)
        os.chdir(project_dir)
        push_option = ''
        if has_option:
            remote = get_remote(project_dir)
            actual_branch = get_actual_branch(project_dir)
            push_option = ' -u {0} {1}'.format(remote, actual_branch)

        os.system('git {0} {1}'.format(Command.PUSH.value, push_option))


def checkout(target_branch):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        os.system('git {0} {1}'.format(Command.CHECKOUT.value, target_branch))


def status():
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        r = os.popen('git status -s')
        lines = r.read().splitlines(False)
        if len(lines) == 0:
            r2 = os.popen('git status')
            lines2 = r2.read().splitlines(False)
            msg = None
            for line in lines2:
                if line.find('All conflicts fixed but you are still merging') != -1:
                    msg = ('Project {0} need to commit (All conflicts fixed but you are still merging)'.format(
                        project_name))
                if line.find('use "git pull"') != -1:
                    msg = ('Project {0} need to pull'.format(project_name))
                elif line.find('Your branch is ahead of') != -1:
                    msg = ('Project {0} need to push'.format(project_name))
                elif line.find('detached at') != -1:
                    print_with_color('Project {0}/'.format(project_name), PrintColor.YELLOW)
                    msg = '\t{0}'.format(line)
                    break
                # other situations
            if msg is None:
                print_with_color('Project {0} is clean'.format(project_name))
            else:
                print_with_color(msg, PrintColor.RED)
            continue
        else:
            print_with_color('Project {0}/'.format(project_name), PrintColor.YELLOW)
        for line in lines:
            status_file = line.rsplit(" ", 1)
            print('\t{0}{1}{2} {3}'.format(PrintColor.RED, status_file[0], PrintColor.END, status_file[1]))


def branch():
    target_path = get_parent_dir()
    branch_map = {}
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        r = os.popen('git branch')
        lines = r.read().splitlines(False)
        for line in lines:
            if line.startswith('*'):
                current_branch = line[2:]
                if current_branch in branch_map:
                    branch_map[current_branch].append(project_name)
                else:
                    branch_map[current_branch] = [project_name]
                break
    length = len(branch_map)
    if length > 0:
        if length == 1:
            print('all projects in branch', end=' ')
            print_with_color(next(iter(branch_map)), PrintColor.GREEN)
        else:
            for key, value in branch_map.items():
                print(f"----{key}({len(value)})----:\n\t{value}\n")


def merge(source_branch):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        os.system('git {0} {1}'.format(Command.MERGE.value, source_branch))


def execute_cfb(branch_name, need_push=False):
    # 批量新建
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        os.chdir(project_dir)
        os.system('git checkout -b {0}'.format(branch_name))

    # commit and push
    os.system('git commit -m "update manifest branch" {0}'.format(MANIFEST_NAME))

    if need_push:
        push(True)


def execute_raw_command(raw_command):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        os.system(raw_command)


# 删除分支
def delete_branch(branch_name, is_remote=False):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        if is_remote:
            os.system('git push {0} --delete {1}'.format(get_remote(project_dir), branch_name))
        else:
            os.system('git branch -d {0}'.format(branch_name))


def repos_help():
    txt = \
        """
        -h or --help:       输出帮助文档
        -c :                对所有模块执行自定义 git 命令, 例如: -c git status.
        -d :                删除本地分支
        -r :                删除远程分支
        ------------------------------------------------------------------------
        status              聚合展示所有模块的仓库状态
        pull or sync        对所有模块执行 git pull
        push [-u]           对所有模块执行 git push, 如果 -u 则执行 git push -u remote branch
        checkout [branch]   对所有模块执行 git checkout
        branch              聚合展示所有模块的当前分支
        merge               对所有模块执行 git merge
        cfb [branch][-p]    统一创建 feature 分支. 先修改 repos_manifest.xml 里的 branch 值，然后 commit, -p 表示推送到远程
        """
    print(txt)


def execute():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'chd:r:', ['help'])

        for name, value in options:
            if name == '-c':
                raw_git_command = ' '.join(args)
                execute_raw_command(raw_git_command)
                return
            elif name in ('-h', '--help'):
                repos_help()
                return
            elif name == '-d':
                delete_branch(value)
                return
            elif name == '-r':
                delete_branch(value, True)
            else:
                print_with_color('error: unknown switch "{0}"'.format(name))
                return

        for arg in args:
            if arg == Command.PULL.value or arg == 'sync':
                # -b branch_name -d custom_dir
                command_d = '-d'
                custom_dir = None
                if command_d in args:
                    d_index = args.index(command_d)
                    if len(args) > d_index + 1:
                        custom_dir = args[d_index + 1]
                    else:
                        print_with_color('err: command -d must set directory, like: -d "C:\\Program Files (x86)"',
                                         PrintColor.RED)
                        sys.exit(-1)

                final_branch = None
                # 判断当前文件夹是否是 git 目录，优先使用此仓库 branch
                current_dir = os.path.abspath(os.path.dirname(__file__))
                if os.path.exists(os.path.join(current_dir, '.git')):
                    final_branch = get_actual_branch(current_dir)

                command_b = '-b'
                if final_branch is None:
                    if command_b in args:
                        b_index = args.index(command_b)
                        if len(args) > b_index + 1:
                            final_branch = args[b_index + 1]
                        else:
                            print_with_color('err: command -b must set branch_name, like: -b master', PrintColor.RED)
                            sys.exit(-1)

                pull(custom_dir, final_branch)
                break
            elif arg == Command.PUSH.value:
                push('-u' in args)
                break
            elif arg == Command.BRANCH.value:
                branch()
                break
            elif arg == Command.STATUS.value:
                status()
                break
            elif arg == Command.CHECKOUT.value:
                if len(args) > 1:
                    target_branch = args[1]
                    checkout(target_branch)
                else:
                    print_with_color('err: git checkout command must contain target branch', PrintColor.RED)
                break
            elif arg == Command.MERGE.value:
                if len(args) > 1:
                    source_branch = args[1]
                    merge(source_branch)
                else:
                    print_with_color('err: git merge command must contain source branch', PrintColor.RED)
                break
            elif arg == 'cfb':
                if len(args) > 1:
                    new_branch = args[1]
                    execute_cfb(new_branch, '-p' in args)
                else:
                    print_with_color('err: cfb command must contain new branch name', PrintColor.RED)
                break
            else:
                print_with_color("err: unsupported command '{0}', see 'python repos.py -h or --help'".format(arg),
                                 PrintColor.RED)
    except getopt.GetoptError as err:
        print_with_color("err: {0}, see 'python repos.py -h or --help'".format(err), PrintColor.RED)
        sys.exit(-1)


def init():
    global manifest_dir
    manifest_dir = os.getcwd()


def main():
    # Ctrl+C 会触发 SIGINT 信号
    signal.signal(signal.SIGINT, signal_handler)
    init()
    parse_manifest()
    execute()


if __name__ == '__main__':
    main()
