#!/usr/bin/python3
# coding=utf-8
# -*- coding：utf-8 -*-
import xml.dom.minidom
import os
import sys
import time
import shutil
import signal
import getopt
import io
from xml.etree import ElementTree as ET
from os.path import expanduser
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

type = sys.getdefaultencoding()
FILE_NOT_EXIST = 1
XML_CONFIG_ERROR = 2
ARGUMENT_ERROR = 3

# 当前项目的根目录
curProjectDir = None
# 当前使用的配置文件路径
configFilePath = None
# 当前项目所拥有的所有module
curModules = []
# 当前配置文件中的所有项目
curProjects = []
# 当前项目的每个模块的名称和地址的映射
namePath = {}
Tree = None
checkCurProjectCmds = ['project', 'dp', '-t', 'update', 'update2']


def prRed(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[91m {}\033[00m".format(res),flush=True)


def prGreen(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[92m {}\033[00m".format(res),flush=True)


def prLightPurple(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[94m {}\033[00m".format(res),flush=True)


def prPurple(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[95m {}\033[00m".format(res),flush=True)


def prCyan(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[96m {}\033[00m".format(res),flush=True)


def prLightGray(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[97m {}\033[00m".format(res),flush=True)


def prBlack(prt):
    global type
    res = prt.encode('utf-8').decode(type)
    print("\033[98m {}\033[00m".format(res),flush=True)


# 按下ctrl+c时触发
def handler(signal_num, frame):
    sys.exit(signal_num)


class Config:
    enter = True
    # 是否采用交互模式，某些命令如果采用交互模式会在命令执行前进行提醒，如果关闭就不会提醒
    isInteractive = False

class Project:
    name = ""
    path = ""


class Module:
    path = None
    branch = None
    init_branch = None
    work_branch = None
    git = None
    name = None
    xml_element = None

    def string(self):
        print("Name：" + self.name)
        print("Branch:" + self.branch)
        print("git:" + self.git)
        print("path:" + self.path)
        print()


config = Config()


def check_cur_project(cmd):
    global checkCurProjectCmds
    global curProjectDir
    if checkCurProjectCmds.count(cmd) != 0:
        return
    if curProjectDir is None:
        prRed("You should specify a right project name in 'curProject'!")
        sys.exit(XML_CONFIG_ERROR)
    if not os.path.exists(curProjectDir):
        print("Wrong path in project,do you want to make it(%s)?(y/n):" % curProjectDir)
        ans = input()
        if ans != "y":
            sys.exit(XML_CONFIG_ERROR)
        else:
            os.mkdir(curProjectDir)


# 检查project tag配置是否正确
def check_project(project):
    if project.get("path") is None or project.get("name") is None:
        print("Your project lack name or path!")
        sys.exit(XML_CONFIG_ERROR)


def check_module(mod):
    if (mod.find("name") is None) or (mod.find("initBranch") is None) or (mod.find("git") is None):
        print("Your module lack name or initBranch or git tag! ")
        sys.exit(XML_CONFIG_ERROR)


def get_all_module(project):
    res = []
    global namePath
    modules = project.findall("module")
    for mod in modules:
        check_module(mod)
        mod_config = Module()
        mod_config.name = mod.find("name").text
        mod_config.init_branch = mod.find("initBranch").text
        mod_config.work_branch = mod.find("workBranch").text
        mod_config.git = mod.find("git").text
        mod_config.path = curProjectDir + "/" + mod_config.name
        mod_config.xml_element = mod
        namePath[mod_config.name] = mod_config.path
        res.append(mod_config)
    return res


# 为每个模块执行命令
def execute_cmd(cmd, is_skip_no_dir=True):
    global curProjectDir
    global config
    for index in range(len(curModules)):
        curMod = curModules[index]
        if config.enter:
            prRed("\nNext is module[%s],s to skip,n to stop,enter to continue:" % curMod.name)
            ans = input()
            if ans == 's':
                continue
            elif ans == 'n':
                return
        prGreen( '---------%s-----------' % curMod.path)
        # 对应的目录存在，则进入到该目录中去执行
        if os.path.exists(curMod.path):
            os.chdir(curMod.path)
            # 如果传入的是命令列表，则取出每个模块对应的命令
            if isinstance(cmd, list):
                cur_cmd = cmd[index]
            # 如果传入的命令是单条命令，则直接执行
            else:
                cur_cmd = cmd
            os.system(cur_cmd)
            print(flush=True)
        # 对应目录不存在
        else:
            # 跳过该命令
            if is_skip_no_dir:
                prLightPurple("This module does't exist!")
            # 在根目录执行该命令
            else:
                os.chdir(curProjectDir)
                # 如果传入的是命令列表，则取出每个模块对应的命令
                if isinstance(cmd, list):
                    cur_cmd = cmd[index]
                # 如果传入的命令是单条命令，则直接执行
                else:
                    cur_cmd = cmd
                os.system(cur_cmd)
                print(flush=True)
    return


def get_tree():
    global Tree
    global configFilePath
    # 默认取所在目录下的配置文件
    configFilePath = os.path.abspath(".") + "/.mgit.xml"
    # 全局配置文件
    globalFilePath = os.path.join(expanduser("~"), ".mgit.xml")
    if not os.path.exists(configFilePath):
        if not os.path.exists(globalFilePath):
            prRed("Can't find .mgit.xml file in your home directory nor project directory!")
            sys.exit(FILE_NOT_EXIST)
        else:
            configFilePath = globalFilePath
    try:
        Tree = ET.parse(configFilePath)
    except xml.etree.ElementTree.ParseError:
        prRed("You should configure your .mgit.xml right!\n" + "path:" + configFilePath)
        sys.exit(XML_CONFIG_ERROR)


# 从xml中解析信息
def load_info():
    global curProjectDir
    global curModules
    global Tree
    global configFilePath
    get_tree()
    root = Tree.getroot()
    cur_project_name = root.get("curProject")
    if cur_project_name is None:
        print("You didn't set a curProject tag!")
        sys.exit(XML_CONFIG_ERROR)
    all_projects = root.findall("project")
    # 查找当前使用的是那个project
    for project in all_projects:
        check_project(project)
        # 顺便记录下各个项目的信息
        p = Project()
        p.name = project.get("name")
        p.path = project.get("path")
        curProjects.append(p)
        if len(all_projects) == 1 or project.get("name") == cur_project_name:
            # 有本地配置文件，path就是当前目录的父目录
            if os.path.exists("./.mgit.xml") and os.path.abspath(".") != os.path.expanduser("~"):
                curProjectDir = os.path.abspath("../")
            else:
                curProjectDir = project.get("path")
            curModules = get_all_module(project)
    if len(sys.argv) > 1:
        check_cur_project(sys.argv[1])
    # 加载配置信息
    global config
    cfg_element = root.find("config")
    if cfg_element is not None:
        enter = cfg_element.find("enter")
        if enter is not None and enter.text is not None:
            if enter.text.lower() == "true":
                config.enter = True
            else:
                config.enter = False
        is_interactive = cfg_element.find("interactive")
        if is_interactive is not None and is_interactive.text is not None:
            if is_interactive.text.lower() == "true":
                config.isInteractive = True
            else:
                config.isInteractive = False



# 修改当前工作的分支
def change_branch(is_init_branch, branch_name, module_name):
    global Tree
    root = Tree.getroot()
    cur_project_name = root.get("curProject")
    all_projects = root.findall("project")
    # 查找当前使用的是那个project
    for project in all_projects:
        if project.get("name") != cur_project_name:
            continue
        modules = project.findall("module")
        for mod in modules:
            if is_init_branch:
                tag = mod.find("initBranch")
            else:
                tag = mod.find("workBranch")
            name = mod.find("name")
            if module_name is not None:
                if name.text == module_name:
                    tag.text = branch_name
            else:
                tag.text = branch_name
    Tree.write(configFilePath)


def get_branches():
    for curMod in curModules:
        if not os.path.exists(curMod.path):
            continue
        os.chdir(curMod.path)
        r = os.popen('git branch')
        lines = r.read().splitlines(False)
        for line in lines:
            if line.startswith('*'):
                curMod.branch = line[2:]
    return


def pull():
    global config
    if config.isInteractive is False:
        execute_cmd('git pull')
        return
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git pull')


def push():
    if config.isInteractive is False:
        execute_cmd('git push')
        return
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git push')


def checkout(new_branch):
    global curProjectDir
    if len(sys.argv) < 3:
        print("Please specific a branch to checkout!")
        return
    elif len(sys.argv) == 3:
        execute_cmd('git checkout ' + new_branch)
    elif len(sys.argv) > 3:
        module_name = sys.argv[3]
        # 切换某个仓库所在分支
        module_path = os.path.join(curProjectDir, module_name)
        os.chdir(module_path)
        os.system('git checkout ' + new_branch)


def add():
    if config.isInteractive is False:
        execute_cmd('git add -A')
        return
    print("Are you sure you want to add all changed files to stage?(y/n)")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git add -A')


def branch():
    for curMod in curModules:
        #prGreen(curMod.name + " : "+curMod.branch)
        if curMod.name is None or curMod.branch is None:
            return
        prGreen("{:<40}:  {:<40}".format(curMod.name,curMod.branch))


def log(module_name):
    if module_name is None:
        execute_cmd('git log')
    elif module_name not in namePath:
        print("The module name is wrong!")
        return
    else:
        module_path = namePath[module_name]
        os.chdir(module_path)
        os.system('git log')


def status(is_detail):
    if is_detail:
        # 详情模式
        execute_cmd('git status')
        return
    for curMod in curModules:
        if not os.path.exists(curMod.path):
            continue
        os.chdir(curMod.path)
        r = os.popen('git status')
        lines = r.read().splitlines(False)
        need_operation = ""
        has_clean_show = False
        for line in lines:
            if line.find('use "git pull"') != -1:
                need_operation += " | need pull"
            elif line.find('use "git add') != -1 or line.startswith('Untracked files'):
                if need_operation.find('need add') != -1:
                    continue
                need_operation += " | need add"
            elif line.find("Changes to be committed") != -1:
                need_operation += " | need commit"
            elif line.find('use "git push') != -1:
                need_operation += " | need push"
            elif line.find('nothing to commit, working directory clean') != -1:
                has_clean_show = True
        if len(need_operation) == 0:
            if has_clean_show:
                prGreen("{:<40}:  {}".format(curMod.name, 'clean'))
                continue
            prRed("{:<40}:  {}".format(curMod.name, 'use "mgit status -d"'))
            continue
        prRed("{:<40}:  {}".format(curMod.name, need_operation[3:]))


def switch_project(new_project):
    get_tree()
    # 设置当前使用的工程名称
    all_projects = Tree.getroot().findall("project")
    # 查找当前使用的是那个project
    has_project = False
    for project in all_projects:
        if project.get("name") == new_project:
            has_project = True
    if not has_project:
        prRed("Wrong project name")
        sys.exit(XML_CONFIG_ERROR)
    Tree.getroot().set("curProject", new_project)
    Tree.write(configFilePath)
    print("Switch to project: " + new_project)


def clone():
    global curProjectDir
    print(curProjectDir)
    if len(os.listdir(curProjectDir)) != 0:
        print("Directory: %s isn't empty,do you want to empty it?(y/n):" % curProjectDir)
        answer = input()
        if answer != 'y':
            return
        shutil.rmtree(curProjectDir)
        os.mkdir(curProjectDir)
    cmds = []
    for curMod in curModules:
        cmd = 'git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name
        cmds.append(cmd)
        # os.system('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name)
        # if config.enter:
        #     print("\nPress enter to continue,q to quit ")
        #     ans = input()
        #     if ans == 'q':
        #         return
    execute_cmd(cmds, False)

# 更新配置文件后使用次命令来更新代码，主要实现：能够克隆新加的仓库，能够pull每个已有仓库的代码
def update():
    global curProjectDir
    if not os.path.exists(curProjectDir):
        os.mkdir(curProjectDir)
    for curMod in curModules:
        os.chdir(curProjectDir)
        cur_mod_path = os.path.join(curProjectDir, curMod.name)
        cur_mod_git_pat = os.path.join(cur_mod_path, '.git')
        if os.path.exists(cur_mod_git_pat):
            # 正常情况下pull就好
            os.chdir(cur_mod_path)
            os.system('git pull')
        elif os.path.exists(cur_mod_path):
            # 仓库在，但.git目录没有了，要删掉旧仓库,从新拉
            shutil.rmtree(cur_mod_path)
            os.system('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name)
        else:
            os.system('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name)


# 与update功能保持一致，增加打印输出流
def update2():
    global curProjectDir
    if not os.path.exists(curProjectDir):
        os.mkdir(curProjectDir)
    for curMod in curModules:
        os.chdir(curProjectDir)
        cur_mod_path = os.path.join(curProjectDir, curMod.name)
        cur_mod_git_pat = os.path.join(cur_mod_path, '.git')
        if os.path.exists(cur_mod_git_pat):
            # 正常情况下pull就好
            os.chdir(cur_mod_path)
            for line in os.popen('git pull'):
                print(line, flush=True)
        elif os.path.exists(cur_mod_path):
            # 仓库在，但.git目录没有了，要删掉旧仓库,从新拉
            shutil.rmtree(cur_mod_path)
            for line in os.popen('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name):
                print(line, flush=True)
        else:
            for line in os.popen('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name):
                print(line, flush=True)


# 打印当前工程所在路径
def path():
    print(curProjectDir)


# 遍历每一个模块然后进行相应的操作
def each():
    for curMod in curModules:
        prGreen("---------%s-----------" % curMod.path)

        if not os.path.exists(curMod.path):
            continue
        os.chdir(curMod.path)
        os.system('git status')
        prGreen("\n( " + curMod.name + " :q for quit,n  or enter for next or others for command to execute)")
        print(":", end='')
        cmd = input()
        while cmd != 'q' and cmd != 'n' and cmd != '':
            print("---------%s-----------" % curMod.path)
            os.system(cmd)
            prGreen("\n(q for quit,n or enter for next or others for command to execute)")
            print(":", end='')
            cmd = input()
        if cmd == 'q':
            sys.exit(0)
        # 继续执行下一个模块的操作
        elif cmd == 'n':
            print("\n\n")
            continue
        else:
            print("\n\n")
            continue


def customer_cmd(cmd):
    print(cmd)
    execute_cmd(cmd)


# 检出该项目的初始分支或工作分支
def checkout_init_or_work_branch(is_init_branch=True):
    if config.isInteractive is True:
        prRed("Please make sure you commit all your files(y/n):")
        ans = input()
        if ans == 'n':
            return
    cmds = []
    global curModules
    for index in range(len(curModules)):
        mod = curModules[index]
        if is_init_branch:
            cmd = "git checkout " + mod.init_branch
        else:
            cmd = "git checkout " + mod.work_branch
        cmds.append(cmd)
    execute_cmd(cmds)


# 添加一个新模块
def add_module(module_name):
    global curProjectDir
    for mod in curModules:
        if module_name == mod.name:
            os.chdir(curProjectDir)
            cmd = 'git clone -b ' + mod.init_branch + ' ' + mod.git + '  ' + mod.name
            os.system(cmd)
            return
    prRed("Wrong module name")


# 大致列出当前分支信息
def list_info():
    global curModules
    for mod in curModules:
        prGreen("-------------------------------------------------------")
        print("name:         " + mod.name)
        print("work branch:  " + mod.work_branch)
        print("init branch:  " + mod.init_branch)
        print("git:          " + mod.git)
        print("\n")


def list_project():
    for p in curProjects:
        prGreen("-----------------------------------------")
        prRed(p.name)
        print(p.path)


def help():
    txt = \
        """
        -h or --help:                  Print the help content.
        -t or --target [project name]: switch the working project.
        -f or --force:                 Force to overwrite the 'enter' tag in xml file,and always opposite. 
        -c or --command:[custom cmd]:  Execute the customer git commands for all modules,for example: -c git status.
        ---------------------------------------------------------------------------------------
        add                 Add files of all the module to the index,just like 'git add'.
        status [-d]         Show the working tree status of every module,just like 'git status',and '-d' show details.
        pull                Fetch from and integrate with another repository or a local branch
                                for every module,just like 'git pull'.
        push                Update remote refs along with associated objects for every module, 
                                just like 'git push'.
        checkout [branch]   Switch the branches of all the modules to a new branch.
        branch              Print all the branches of every module.
        log [module]        Print the log of the specific module,and if module is empty,execute 'git log' 
                                for every module.
        clone               Clone a new project to local,you should config it in the .mgit.xml first.
        path                Print the directory of current working project.
        each                Execute commands in interaction mode.
        wb                  Switch the branches of all the modules to the work branch configured 
                                in the .mgit.xml.
        ib                  Switch the branches of all the modules to the init branch configured 
                                in the .mgit.xml.
        am [new module]     Add a new module to project,you should config the module in .mgit.xml first.
        list                List the information of every module.
        project             List all the projects configured in the .mgit.xml
        cib [branch_name] [module_name]
                            Change "initBranch" tag in configure file,and if module_name is specified,would only
                                change the tag in the module.
                                
        cwb [branch_name] [module_name]
                            Change "workBranch" tag in configure file,and if module_name is specified,would only
                                change the tag in the module.
        merge [status]      if status is true  or not specified ,would merge work branch to init branch ,if false,merge init branch
                                to work branch.
        dm    [module_name] Delete the module from configuration file.
        dp    [project_name] Delete the project form configuration file.
        """
    print(txt)


# 分支合并
def merge(is_to_init):
    cmds = []
    for curMod in curModules:
        # 将work分支合并到init分支
        if is_to_init:
            cmd = 'git checkout  ' + curMod.init_branch + '&& git merge ' + curMod.work_branch
        else:
            cmd = 'git checkout  ' + curMod.work_branch + '&& git merge ' + curMod.init_branch
        cmds.append(cmd)
        # os.system('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name)
        # if config.enter:
        #     print("\nPress enter to continue,q to quit ")
        #     ans = input()
        #     if ans == 'q':
        #         return
    execute_cmd(cmds, False)


# 删除module
def delete_module(module_name):
    global Tree
    root = Tree.getroot()
    cur_project_name = root.get("curProject")
    all_projects = root.findall("project")
    # 查找当前使用的是那个project
    for project in all_projects:
        if project.get("name") != cur_project_name:
            continue
        modules = project.findall("module")
        for mod in modules:
            name = mod.find("name").text
            if module_name == name:
                print("Are you sure to delete this module?(y/n):", end='')
                ans = input()
                if 'y' == ans:
                    project.remove(mod)
                    prGreen("Delete module successfully!")
                    Tree.write(configFilePath)
                return
        prRed("No such module!")


# 删除工程
def delete_project(project_name):
    global Tree
    root = Tree.getroot()
    all_projects = root.findall("project")
    for project in all_projects:
        name = project.get("name")
        if name != project_name:
            continue
        print("Are you sure to delete this project(" + name + ")?(y/n):", end='')
        ans = input()
        if 'y' == ans:
            root.remove(project)
            Tree.write(configFilePath)
            prGreen("Delete project successfully!")
            Tree.write(configFilePath)
            return
    prRed("No such project!")


def cmd_dispatch():
    global curModules
    global needCheckCurProject
    try:
        options, args = getopt.getopt(sys.argv[1:], "hft:c", ["help", "target=", "command"])
        for name, value in options:
            if name in ("-h", "--help"):
                # help
                help()
                break
            elif name in ("-t", "--target"):
                switch_project(value)
                break
            elif name in ("-f", "--force"):
                config.enter = not config.enter
            elif name in ("-c", "--command"):
                customer_command = ""
                for i in args:
                    customer_command += (i + " ")
                customer_cmd(customer_command)
                return
        for i in range(len(args)):
            cmd = args[i]
            if cmd == "status":
                if i+1 < len(args) and args[i+1] == '-d':
                    status(True)
                else:
                    status(False)
                break
            elif cmd == "pull":
                get_branches()
                pull()
                break
            elif cmd == "push":
                get_branches()
                push()
                break
            elif cmd == "checkout":
                if i + 1 >= len(args):
                    raise getopt.GetoptError('Wrong argument')
                new_branch = args[i + 1]
                get_branches()
                checkout(new_branch)
                break
            elif cmd == "add":
                get_branches()
                add()
                break
            elif cmd == "branch":
                get_branches()
                branch()
                break
            elif cmd == "log":
                get_branches()
                if i + 1 >= len(args):
                    log(None)
                else:
                    log(args[i + 1])
                break
            elif cmd == "clone":
                clone()
                break
            elif cmd == "path":
                needCheckCurProject = False
                path()
                break
            elif cmd == "each":
                each()
                break
            elif cmd == "wb":
                checkout_init_or_work_branch(False)
                break
            elif cmd == "ib":
                checkout_init_or_work_branch(True)
                break
            elif cmd == "am":
                if i + 1 >= len(args):
                    prRed("Wrong argument,please specify a module name you want to add")
                else:
                    add_module(args[i + 1])
                break
            elif cmd == "list":
                list_info()
                break
            elif cmd == "project":
                needCheckCurProject = False
                list_project()
                break
            elif cmd == "cib":

                if i + 1 >= len(args):
                    prRed("Wrong argument,please specify a branch name you want to change!")
                elif len(args) == 2:
                    change_branch(True, args[i + 1], None)
                elif len(args) == 3:
                    change_branch(True, args[i + 1], args[i + 2])
                else:
                    prGreen("Warning:you input too mush parameters,the redundant parameters will be ignored")
                    change_branch(True, args[i + 1], args[i + 2])
                break
            elif cmd == "cwb":
                if i + 1 >= len(args):
                    prRed("Wrong argument,please specify a branch name you want to change!")
                elif len(args) == 2:
                    change_branch(False, args[i + 1], None)
                elif len(args) == 3:
                    change_branch(False, args[i + 1], args[i + 2])
                else:
                    prGreen("Warning:you input too mush parameters,the redundant parameters will be ignored")
                    change_branch(False, args[i + 1], args[i + 2])
                break
            elif cmd == "merge":
                if i + 1 >= len(args):
                    merge(True)
                else:
                    merge(args[i + 1].lower() == 'true')
                break
            elif cmd == "dm":
                if len(args) < 2:
                    prRed("No module name!")
                else:
                    delete_module(args[i + 1])
                break
            elif cmd == "dp":
                needCheckCurProject = False
                if len(args) < 2:
                    prRed("No project name!")
                else:
                    delete_project(args[i + 1])
                break
            elif cmd == "update":
                update()
            elif cmd == "update2":
                update2()
            else:
                prRed("Wrong argument,please refer to '-h or --help'")
    except getopt.GetoptError:
        prRed("Wrong argument,please refer to '-h or --help'")


def main():
    signal.signal(signal.SIGINT, handler)
    load_info()
    cmd_dispatch()


main()
