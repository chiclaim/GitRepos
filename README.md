# Repos
统一管理 Git 多仓库，使用上比 Google Repo 更加便利

# 背景
- repo 繁琐问题，需要单独管理 Manifest 分支
- repo 不能跨多个 remote
- Google repo 的 status 命令输出信息过多
- 简化迭代时新建分支流程，提高效率


# 使用说明

## 编辑 repos_manifest.xml

将需要管理的 git 仓库 url 放在 `repos_manifest.xml` 中，如：

```
<manifest>
    <project name="Repos3" git="git@github.com:chiclaim/Repos.git" />
    <project name="Repos2" git="git@github.com:chiclaim/Repos.git" />
    <project name="Repos1" git="git@github.com:chiclaim/Repos.git" />
</manifest>
```

## 复制脚本和清单文件到你的主工程（建议）

一般 iOS、Android 都是模块化开发，可以将脚本文件 `repos.py` 和 `repos_manifest.xml` 拷贝到主工程 `根目录`，然后提交。

第一次同步代码时，其他仓库默认会使用当前仓库所在的分支。也可以手动指定分支：`python repos.py sync -b master`

例如，你的项目名字叫做 GitHubClient，这个是你的主工程，你的代码是多模块组成的（非单工程）的。GitHubClient 这个主工程依赖其他模块。

所有的仓库在 `repos_manifest.xml` 中配置：

```
<manifest>
    <!--主工程-->
    <project name="Repos1" git="git@github.com:chiclaim/GitHubClient.git" />
    <!--趋势模块-->
    <project name="Repos3" git="git@github.com:chiclaim/Trending.git" />
    <!--用户模块-->
    <project name="Repos2" git="git@github.com:chiclaim/User.git" />
    <!--省略其他模块-->
</manifest>
```

假设文件 `repos.py` 和 `repos_manifest.xml` 已经在你的 GitHubClient `根目录` 了

如果是第一次拉代码，首先克隆主工程：

```
git clone -b your_branch git@github.com:chiclaim/GitHubClient.git GitHubClient
```

然后进入 GitHubClient 目录，执行如下命令，：

```
python repos.py sync -b master
```


## 常用命令

- python repos.py cfb `new_branch_name` -p

    新的需求，我们需要统一创建 feature 分支（cfb 是 create feature branch 简称），-p 表示推送到远程，没有该选项表示创建本地分支

- python repos.py sync

    同步所有模块代码，也可以自定义代码输出路径例如：`python repos.py sync -d "C:\xxx"` 路径为绝对路径
    与此同时，还可以指定 branch 例如：`python3 repos.py sync -d "C:\Program Files (x86)" -b master`

- python repos.py pull

    同 `python repos.py sync`

- python repos.py push

    对所有模块执行 git push

- python repos.py push -u

    如果没有指定跟踪的分支，加上 -u 即可。执行 git push -u remote branch

- python repos.py checkout `your_branch_name`

    对所有模块执行 git checkout

- python repos.py branch

    聚合展示所有模块的当前分支（一般开发前，要确保所有的模块都在统一的分支上）

- python repos.py merge `source_branch`

    合并代码，对所有模块执行 git merge

- python repos.py -h

    帮助文档

- python repos.py -c `git_command`

    对所有模块执行自定义 git 命令，例如: -c git cherry.

- python repos.py -d

    删除本地分支

- python repos.py -r

    删除远程分支


# TODOs

- [ ] Windows 系统下命令输出日志没有颜色高亮（可以使用 git bash），Mac 和 Linux 会有颜色高亮展示
- [ ] 分组展示当前所有模块的分支详细情况
- [x] 聚合展示当前所有模块的分支情况，快速查看所有模块是否在统一的分支上
- [x] 精确展示 status 日志
- [x] 统一创建 feature 分支
- [x] pull
- [x] push
- [x] 执行自定义 git 命令
- [x] 删除远程、本地分支
- [x] 合并分支
