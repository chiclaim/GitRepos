# Repos
统一管理 Git 多仓库，使用上比 Google Repo 更加便利

# 背景
- Google repo 繁琐问题，需要单独管理 Manifest 分支，开发时常常忘记
- Google repo 不能跨多个 remote
- Google repo 对 Windows 系统支持不是很友好
- Google repo 的 status 命令输出信息过多

于是基于 Python3 开发一套关于批量管理多个 git 仓库的工具。


# 使用说明

## 编辑 template_module_manifest.json

将需要管理的 git 仓库 url 放在 `template_module_manifest.json` 中，如：

```
{
  "modules": [
    {
      "project_id": 0,
      "git": "git@github.com:chiclaim/Repos.git",
      "branch_boss": true,
      "moduleName": "Repos"
    },
    {
      "project_id": 0,
      "git": "git@github.com:chiclaim/GitRepos.git",
      "moduleName": "Repos1"
    },
    {
      "project_id": 0,
      "git": "git@github.com:chiclaim/GitRepos.git",
      "moduleName": "Repos2"
    }
  ]
}
```

字段说明：

- project_id 用于给 gitlab 批量创建 merge request
- git 工程等的 git url 地址
- moduleName 工程的名称
- branch_boss 必须要存在一个 branch_boss = true 的项目，其他的项目均以该组件的 branch 作为标准，例如 某个组件的 branch_boss=true，其他组件执行 git clone 时都会以该分支为准。

## 配置环境变量

```
# 1. clone 脚本
git clone git@github.com:chiclaim/GitRepos.git

# 2. 配置环境变量(MacOS 为例)
open ~/.bash_profile

# 3. 添加如下内容
export REPOS_HOME=你刚刚克隆的脚本地址
export PATH=${PATH}:${REPOS_HOME}

# 终端运行 (或新起一个终端)
source ~/.bash_profile

# 就可以使用 repos 命令
repos --help

# 如果需要使用自动创建 merge request（repos cmr $target_branch）需要设置你的 private-token
repos --set-private-token your-token

```

## 使用步骤

配置完环境变量后，您就可以把 repos 当做 git 命令一样使用。

### clone 代码

使用 git 时 clone 代码，我们会在目标目录执行 git clone git_url 命令

同理，使用 repos clone 代码，也需要在目标目录执行 repos init git_url module_manifest_json_path

repos 需要所有 git 项目的 json 配置文件，repos init 的第一个参数是配置文件所在的仓库的git url，第二个参数就是配置文件的相对路径（也可以绝对路径）

例如:

```
repos init git@github.com:chiclaim/GitRepos.git GitRepos/template_module_manifest.json
```

最后执行

```
repos sync
```

repos 会帮你将 template_module_manifest.json 配置的所有组件，全部 clone 到目标目录（执行 repos init 的目录）

### 将已经存在的项目交给 repos 管理

如果您的项目已经存在，可以执行如下命令：

```
repos init-exist GitRepos/template_module_manifest.json
```

repos init-exist 的第一个参数是组件配置文件的目录

然后可以尝试执行 repos branch，查看当前所有项目的分支情况

## 命令介绍

repos 和 git 命令一样，你可以在项目目录或任意的子目录执行 repos 命令



- repos init $AppConfig_SSH $manifest_path

    初始化新项目

- repos init-exist $manifest_path

    如果你的工程已经存在，使用 init-exist 初始化

- repos cfb `new_branch_name` -p

    统一创建分支(feature)

- repos sync

    同步所有模块代码

- repos pull

    对所有模块执行 git pull

- repos push

    对所有模块执行 git push

- repos push -u

    如果没有指定跟踪的分支，加上 -u 即可。执行 git push -u remote branch

- repos checkout `your_branch_name`

    对所有模块执行 git checkout

- repos branch

    聚合展示所有模块的当前分支

- repos merge `source_branch`

    对所有模块执行 git merge

- repos -h

    帮助文档

- repos -c `git_command`

    对所有模块执行自定义 git 命令，例如: -c git status.

- repos -d

    删除本地分支

- repos -r

    删除远程分支

- repos diff [branch_name]

    分支对比

- repos cmr $target_branch

    自动为修改的组件提交 merge request,参数说明：
    $target_branch 目标分支，即当前分支 merge 到的分支, 一般为 release/develop/master 分支





# TODOs
- [x] 支持通过配置环境变量的方式，全局可以使用 repos 命令
- [x] 统一删除 feature 分支，避免垃圾分支过多
- [x] 分组展示当前所有模块的分支详细情况
- [x] 聚合展示当前所有模块的分支情况，快速查看所有模块是否在统一的分支上
- [x] 精确展示 status 日志
- [x] 统一创建 feature 分支
- [x] pull
- [x] push
- [x] 执行自定义 git 命令
- [x] 删除远程、本地分支
- [x] 合并分支
