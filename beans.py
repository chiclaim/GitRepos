from enum import Enum


class Project:
    def __init__(self, project_id, name, importSource, git, ignore, isRootProject, isFlutter, version):
        self.id = project_id
        self.name = name
        self.importSource = importSource
        self.git = git
        self.ignore = ignore
        self.isRootProject = isRootProject
        self.isFlutter = isFlutter
        self.version = version


class Command(Enum):
    INIT = 'init'
    INIT_EXIST = "init-exist"
    CONFIG = "config"
    PULL = 'pull'
    PUSH = 'push'
    BRANCH = 'branch'
    CHECKOUT = 'checkout'
    STATUS = 'status'
    MERGE = 'merge'
    UPDATE = 'update'
    CREATE_FEATURE_BRANCH = 'cfb'
    CLEAN = 'clean'
    DIFF = 'diff'
    TAG = 'tag'
    UPDATE_GIT_URL = 'update_git_and_name'
    CREATE_MERGE_REQUEST = 'cmr'
    LIST = 'list'
    CUSTOM = '-c'

