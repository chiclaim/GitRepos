import signal
import sys
import os
import getopt
import string
from enum import Enum
from xml.etree import ElementTree as eTree

MANIFEST_NAME = "repo_manifest.xml"
manifest_dir: string


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

    config = root.find('config')
    check_none(config, 'config 子节点未找到')

    manifest.branch = config.get('branch')
    check_none(manifest.branch, 'config 节点 branch 属性未设置')
    check_empty(manifest.branch, 'branch 不能为空')

    project_list = root.findall('project')
    for project in project_list:
        manifest.projects[project.get('name')] = project.get('git')


def check_project_exist(project_dir, project_name):
    if not os.path.exists(project_dir):
        print_with_color('Project `{0}` is not exist, you may need to sync projects'.format(project_name),
                         PrintColor.RED)
        sys.exit(-1)


# manifest 上一级目录
def get_parent_dir():
    return os.path.dirname(manifest_dir)


# 获取参考的展示分支
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


def pull():
    target_path = get_parent_dir()
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
                elif line.find('use "git push"') != -1:
                    msg = ('Project {0} need to push'.format(project_name))
                # other situations
            if msg is None:
                print_with_color('Project {0} is clean'.format(project_name))
            else:
                print_with_color(msg, PrintColor.YELLOW)
            continue
        else:
            print_with_color('Project {0}/'.format(project_name), PrintColor.YELLOW)
        for line in lines:
            status_file = line.rsplit(" ", 1)
            print('     {0}{1}{2} {3}'.format(PrintColor.RED, status_file[0], PrintColor.END, status_file[1]))


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


def merge(source_branch):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        os.system('git {0} {1}'.format(Command.MERGE.value, source_branch))


def execute_cfb(branch_name):
    # 批量新建
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        os.chdir(project_dir)
        os.system('git checkout -b {0}'.format(branch_name))

    # 工作目录切换到 manifest 所在的目录
    os.chdir(manifest_dir)
    os.system('git checkout -b {0}'.format(branch_name))

    # 修改 branch
    element_tree = manifest_tree()
    root = element_tree.getroot()
    config = root.find('config')
    config.set('branch', branch_name)
    element_tree.write(os.path.abspath(MANIFEST_NAME))

    # commit and push
    os.system('git commit -m "update manifest branch" {0}'.format(MANIFEST_NAME))
    push(True)


def execute_raw_command(raw_command):
    target_path = get_parent_dir()
    for project_name in manifest.projects.keys():
        project_dir = os.path.join(target_path, project_name)
        check_project_exist(project_dir, project_name)
        os.chdir(project_dir)
        os.system(raw_command)


def repos_help():
    txt = \
        """
        -h or --help:       输出帮助文档
        -c :                对所有模块执行自定义 git 命令，例如: -c git status.
        ------------------------------------------------------------------------
        status              聚合展示所有模块的仓库状态
        pull or sync        对所有模块执行 git pull
        push [-u]           对所有模块执行 git push，如果 -u 则执行 git push -u remote branch
        checkout [branch]   对所有模块执行 git checkout
        branch              聚合展示所有模块的当前分支
        merge               对所有模块执行 git merge
        cfb [branch][-p]     创建新分支；会修改 repo_manifest.xml 里的 branch 值；-p 表示推送到远程
        """
    print(txt)


def execute():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'ch', ['help'])

        for name, value in options:
            if name == '-c':
                raw_git_command = ' '.join(args)
                execute_raw_command(raw_git_command)
                return
            elif name in ('-h', '--help'):
                repos_help()
                return
            else:
                print_with_color('error: unknown switch "{0}"'.format(name))
                return

        for arg in args:
            if arg == Command.PULL.value or arg == 'sync':
                pull()
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
                    execute_cfb(new_branch)
                else:
                    print_with_color('err: cfb command must contain new branch name', PrintColor.RED)
                break
            else:
                print_with_color("err: unsupported command '{0}', see 'python repos.py -h or --help'".format(arg),
                                 PrintColor.RED)
    except getopt.GetoptError as err:
        print_with_color("{0}, see 'python repos.py -h or --help'".format(err), PrintColor.RED)
        sys.exit(-1)


def init():
    global manifest_dir
    manifest_dir = os.getcwd()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    init()
    parse_manifest()
    execute()


if __name__ == '__main__':
    main()
