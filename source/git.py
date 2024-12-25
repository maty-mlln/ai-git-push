"""
This module contains functions to interact with Git.
"""

import subprocess
import sys

from format import print_gradient


def is_git_repository() -> bool:
    """
    Check if the current directory is a git repository.
    """
    try:
        subprocess.check_output(['git', 'rev-parse', '--git-dir'],
                                stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def get_changed_files(filter_type: str) -> list[str]:
    """
    Get the list of files that have been added, modified, or deleted.
    """
    result = subprocess.check_output(['git', 'diff', '--cached',
                                      '--name-only',
                                      f'--diff-filter={filter_type}'])
    res_list: list[str] = ["      " +
                           line for line in result.decode().splitlines()]
    return res_list


def is_initial_commit() -> bool:
    """
    Check if the current commit is the initial commit.
    """
    try:
        subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                stderr=subprocess.DEVNULL)
        return False
    except subprocess.CalledProcessError:
        return True


def get_changes_summary() -> str:
    """
    Get the summary of changes in the current commit.
    """
    try:
        if is_initial_commit():
            res = subprocess.check_output(['git', 'diff', '--cached'])
        else:
            res = subprocess.check_output(['git', 'diff', 'HEAD'])
        return '\n'.join(['\t' + line for line in res.decode().splitlines()])
    except subprocess.CalledProcessError as e:
        print_gradient(f"❌ Error: could not get changes summary: {str(e)}",
                       "red_magenta")
        sys.exit(1)
