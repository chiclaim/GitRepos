import json
import os
from xml.etree import ElementTree as eTree

import gitlab

from utils import print_error, config_file_path

key_private_token = "gitlab_private_token"
key_git_server_url = "gitlab_server_url"


def set_private_token_and_url(input_token, git_server_url):
    if input_token is None and git_server_url is None:
        return
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as jsonFile:
            data = json.load(jsonFile)
        if input_token is not None:
            data[key_private_token] = input_token
        if git_server_url is not None:
            data[key_git_server_url] = git_server_url
        with open(config_file_path, "w") as jsonFile:
            json.dump(data, jsonFile)
    else:
        data = {}
        if input_token is not None:
            data[key_private_token] = input_token
        if git_server_url is not None:
            data[key_git_server_url] = git_server_url
        json_dumps = json.dumps(data)
        with open(config_file_path, "w") as jsonFile:
            jsonFile.write(json_dumps)


def __get_gitlab():
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as jsonFile:
            data = json.load(jsonFile)
        input_token = data.get(key_private_token)
        git_server_url = data.get(key_git_server_url)
        if input_token is None or len(input_token.strip()) == 0:
            print_error("please set gitlab private-token with command 'repos config ...'")
        if git_server_url is None or len(git_server_url.strip()) == 0:
            print_error("please set gitlab git-server-url with command 'repos config ...'")
        gl = gitlab.Gitlab(url=git_server_url, private_token=input_token)
        gl.auth()
        return gl
    else:
        print_error("please executing 'repos config ...' to set gitlab parameters")


# 根据 manifest 文件查询组件对应的 project id
def __match_project_id(manifest_path):
    gl = __get_gitlab()
    element_tree = eTree.parse(manifest_path)
    root = element_tree.getroot()
    project_list = root.findall('project')
    for project in project_list:
        projects = gl.projects.list(search=f"{project.get('name')}")
        for p in projects:
            if p.name == project.get('name'):
                print(f"{p.name}  {p.id}")


# 校验 manifest 文件的 project id 是否正确
def __verify_project_id(manifest_path):
    gl = __get_gitlab()
    element_tree = eTree.parse(manifest_path)
    root = element_tree.getroot()
    project_list = root.findall('project')
    for project in project_list:
        projects = gl.projects.list(search=f"{project.get('name')}")
        for p in projects:
            if p.name == project.get('name'):
                if str(p.id) != project.get('id'):
                    print(f"error:the project id of {p.name} is wrong!")


#  创建分支
def create_branch(manifest_path, new_branch_name, source_branch_name):
    gl = __get_gitlab()
    element_tree = eTree.parse(manifest_path)
    root = element_tree.getroot()
    project_list = root.findall('project')
    for project in project_list:
        gitlab_project = gl.projects.get(id=project.get('id'))
        status = gitlab_project.branches.create({'branch': new_branch_name,
                                                 'ref': source_branch_name})
        print(f"{gitlab_project.name} create branch {new_branch_name} {status}")
        return


def parse_manifest(module_manifest_path):
    manifest_file_path = os.path.abspath(module_manifest_path)
    if not os.path.exists(manifest_file_path):
        print_error("当前文件夹找不到{0}文件".format(module_manifest_path))
    else:
        f = open(module_manifest_path)
        data = json.load(f)
        return data['modules']


# created, waiting_for_resource, preparing, pending, running, success, failed, canceled, skipped, manual, scheduled
def __cancel_pipeline(manifest_path):
    gl = __get_gitlab()
    project_list = parse_manifest(manifest_path)
    for project in project_list:
        gitlab_project = gl.projects.get(id=project.get('project_id'))
        ps = gitlab_project.pipelines.list()
        for p in ps:
            if p.status not in ['failed', 'canceled', 'skipped']:
                print(f"{p.id}-{p.status} cancel")
                p.cancel()


def __searchUser():
    gl = __get_gitlab()
    users = gl.users.list(search='kumu')
    for user in users:
        print(f"{user.id} - {user.username} {user.name}")


def create_merge_request(project_id, source_branch, target_branch, title, assignee_id):
    gl = __get_gitlab()
    gitlab_project = gl.projects.get(project_id)
    gitlab_project.mergerequests.create({'source_branch': source_branch,
                                         'target_branch': target_branch,
                                         'title': title,
                                         'assignee_id': assignee_id})


if __name__ == '__main__':
    file_path = 'your module_manifest.json'
    # __searchUser()
    # __verify_project_id(file_path)
    # create_branch(file_path, 'feature/gitlab_api_create', 'master')
    # os.system("python3 ~/repos")
    __cancel_pipeline(file_path)
    # create_merge_request(536, 'feature/module_stand_alone', 'develop', 'merge request to develop', 532) # 532 JiangLi
