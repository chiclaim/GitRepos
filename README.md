# Repos
统一管理 Git 多仓库，使用上比 Google Repo 更加便利

# 背景
- repo 繁琐问题，需要单独管理 Manifest 分支
- repo 不能跨多个 remote
- 简化迭代时新建分支流程，提高效率（相对于公司内部的 git 封装脚本，从 9 条命令简化到 1 条）
- status 不精确问题（公司内部 git 封装脚本）


# 使用说明

- python repos.py cfb `new_branch_name` -p

    统一创建 feature 分支，会修改 repos_manifest.xml 里的 branch 值，然后 commit，-p 表示推送到远程，没有 -p 表示只创建分支

- python repos.py sync

    同步所有模块代码

- python repos.py pull

    对所有模块执行 git pull

- python repos.py push

    对所有模块执行 git push

- python repos.py push -u

    如果没有指定跟踪的分支，加上 -u 即可。执行 git push -u remote branch

- python repos.py checkout `your_branch_name`

    对所有模块执行 git checkout

- python repos.py branch

    聚合展示所有模块的当前分支

- python repos.py merge `source_branch`

    对所有模块执行 git merge

- python repos.py -h

    帮助文档

- python repos.py -c `git_command`

    对所有模块执行自定义 git 命令，例如: -c git status.

- python repos.py -d

    删除本地分支

- python repos.py -r

    删除远程分支




