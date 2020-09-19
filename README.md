# Repos
统一管理 Git 多仓库，使用上比 Google Repo 更加便利

# 背景
- repo 繁琐问题，需要单独管理 Manifest 分支
- repo 不能跨多个 remote
- 简化迭代时新建分支流程，提高效率（相对于公司内部的 git 封装脚本，从 9 条命令简化到 1 条）
- status 不精确问题（公司内部 git 封装脚本）

# 用法
```
    -h or --help:       输出帮助文档
    -c :                对所有模块执行自定义 git 命令，例如: -c git status.
    -d :                删除本地分支
    -r :                删除远程分支
    ------------------------------------------------------------------------
    status              聚合展示所有模块的仓库状态
    pull or sync        对所有模块执行 git pull
    push [-u]           对所有模块执行 git push，如果 -u 则执行 git push -u remote branch
    checkout [branch]   对所有模块执行 git checkout
    branch              聚合展示所有模块的当前分支
    merge               对所有模块执行 git merge
    cfb [branch][-p]    统一创建 feature 分支，会修改 repo_manifest.xml 里的 branch 值，然后 commit，-p 表示推送到远程
```



