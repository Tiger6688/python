# git.py
# Creation 2014-10-23
# Author zrong

"""
.. module:: git
   :platform: Unix, Windows
   :synopsis: git 通用操作。

.. moduleauthor:: zrong(zengrong.net)

"""

import os
import subprocess
from zrong import slog


def call(path, *args):
    """使用 subprocess.check_output 调用 git 命令。

    :param str path: git 仓库文件夹路径。
    :param \*args: git 的附加参数。
    :returns: 错误代码和调用结果。
    :rtype: int
    :rtype: string git 返回的信息，若执行出错则为错误信息。

    """
    returncode = 0
    output = None
    try:
        output = subprocess.check_output(get_args(path, *args), 
                stderr=subprocess.STDOUT,
                universal_newlines=True)
    except subprocess.CalledProcessError as err:
        returncode = err.returncode
        output = err.output
    return returncode, output

def get_args(path, *args):
    """获取可被 subprogress 执行的 git 参数 list。

    :param str path: git 仓库文件夹路径。
    :param \*args: git 的附加参数。

    """
    base = [ 'git' ]
    if path:
        base.append("--git-dir="+os.path.join(path, ".git"))
        base.append("--work-tree="+path)
    for arg in args:
        base.append(arg)
    return base

def isclean(path):
    """检查版本库是否是干净的。

    :param str path: git 仓库文件夹路径。
    :rtype: boolean

    """
    return call(path, 'status', '-s')[1] == ''

def get_branches(path):
    """获取当前所有分支名称的列表。

    :param str path: git 仓库文件夹路径。
    :return: 分支名称列表。当前分支位于列表第一项。
    :rtype: list

    """
    code, output = call(path, 'branch', '--list')
    if code > 0:
        return None
    branches = output.split('\n')
    newbr = [None]
    for br in branches:
        if br:
            if br[0] == '*':
                newbr[0] = br[2:]
            else:
                newbr.append(br[2:])
    return newbr
    
def clone(giturl, gitpath):
    """clone 一个 git 库。

    :param str giturl: git 仓库的 url 地址。
    :param str gitpath: git 仓库保存路径。

    """
    gitArgs = ['git', 'clone', giturl, gitpath]
    slog.info(' '.join(gitArgs))
    return subprocess.call(gitArgs)

def get_hash(path, cut=0):
    """获取可被 git 的 HEAD 的 sha1 值。

    :param str path: git 仓库文件夹路径。
    :param int cut: 包含的 sha1 值的长度。0代表不剪切。
    :returns: 剪切过的 sha1 的值。
    :rtype: str

    """
    code, output = call(path, 'rev-parse', 'HEAD')
    if code > 0:
        return None
    # maybe the string is with a linebreak.
    sha1 = output.strip()
    if cut > 0:
        sha1 = sha1[:7]
    return sha1

def get_commit_times(path):
    """获取提交次数。

    :param str path: git 仓库文件夹路径。
    :returns: 包含所有分支的提交次数。
    :rtype: int

    """
    code, output = call(path, "rev-list", '--all')
    if code > 0:
        return None
    return output.count("\n")

def update_submodules(path, init=True, update=True):
    """更新子模块。

    :param str path: git 仓库文件夹路径。
    :param bool init: 是否初始化子模块。
    :param bool update: 是否更新子模块。

    """
    succ = None
    if init:
        arg = get_args(path, 'submodule', 'init')
        slog.info(' '.join(arg))
        succ = subprocess.call(arg)
        if succ>0:
            slog.error('git execute error!')
            return succ
    if update:
        arg = get_args(path, "submodule", "update")
        slog.info(' '.join(arg))
        succ = subprocess.call(arg)
        if succ>0:
            slog.error('git execute error!')
            return succ
    return succ
