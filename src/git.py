"""
This module contains functions to interact with Git.
"""

import os
import subprocess
import sys

from format import box_print, print_gradient
from llm import ask_llm


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


def _get_changed_files(filter_type: str) -> list[str]:
    """
    Get the list of files that have been added, modified, or deleted.
    """
    result = subprocess.check_output(['git', 'diff', '--cached',
                                      '--name-only',
                                      f'--diff-filter={filter_type}'])
    res_list: list[str] = ["      " +
                           line for line in result.decode().splitlines()]
    return res_list


def _is_initial_commit() -> bool:
    """
    Check if the current commit is the initial commit.
    """
    try:
        subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                stderr=subprocess.DEVNULL)
        return False
    except subprocess.CalledProcessError:
        return True


def _get_changes_summary() -> str:
    """
    Get the summary of changes in the current commit.
    """
    try:
        if _is_initial_commit():
            res = subprocess.check_output(['git', 'diff', '--cached'])
        else:
            res = subprocess.check_output(['git', 'diff', 'HEAD'])
        return '\n'.join(['\t' + line for line in res.decode().splitlines()])
    except subprocess.CalledProcessError as e:
        print_gradient(f"❌ Error: could not get changes summary: {str(e)}",
                       "red_magenta")
        sys.exit(1)


def _get_file_statistics() -> dict[str, tuple[list[str], int]]:
    """
    Get statistics about changed files.
    """
    added_files: list[str] = _get_changed_files('A')
    modified_files: list[str] = _get_changed_files('M')
    deleted_files: list[str] = _get_changed_files('D')
    renamed_files: list[str] = _get_changed_files('R')
    return {
        'added': (added_files, len(added_files)),
        'modified': (modified_files, len(modified_files)),
        'deleted': (deleted_files, len(deleted_files)),
        'renamed': (renamed_files, len(renamed_files))
    }


def _perform_git_commit(commit_message: str) -> None:
    """
    Perform the git commit operation.
    """
    with open('commit_msg.txt', 'w', encoding='utf-8') as f:
        f.write(commit_message)
    subprocess.run(['git', 'commit', '-F', 'commit_msg.txt'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   check=True)
    os.remove('commit_msg.txt')


def _push_to_branch() -> None:
    """
    Push changes to the current branch.
    """
    branch = subprocess.check_output([
        'git', 'branch', '--show-current']).decode().strip()
    print_gradient(f"🚀 Pushing to {branch}...", "cyan_blue")
    push_result = subprocess.run(['git', 'push', 'origin', branch],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 check=False)
    if push_result.returncode == 0:
        print_gradient(f"✅ Successfully pushed to {branch}", "green_lime")
    else:
        print_gradient(f"❌ Error: Failed to push to {branch}: " +
                       f"{push_result.stderr.decode()}", "red_magenta")


def _build_commit_message(message: str,
                          stats: dict[str, tuple[list[str], int]],
                          ai_summary: str) -> str:
    """
    Build the commit message from the given components.
    """
    if message:
        return message
    commit_message: str = f"{ai_summary}\n\nDetailed changes:"
    for category, (files, count) in stats.items():
        if count > 0:
            commit_message += (f"\n\n{category.title()} ({count}):\n" +
                               '\n'.join(files))
    return commit_message


def _get_user_confirmation(commit_message: str) -> bool:
    """
    Get user confirmation for the commit message.
    """
    print_gradient("✅ Successfully generated commit message", "green_lime")
    print_gradient(box_print(commit_message), "light_gray")
    print_gradient("🛎️ Do you want to proceed? [Y/n] ", "yellow_orange", False)
    response = input()
    return response.strip().lower() in ('y', '')


def commit_and_push_changes(message: str = "") -> None:
    """
    Generate a commit message and push to the current branch.
    """
    try:
        stats: dict[str, tuple[list[str], int]] = _get_file_statistics()
        changes_summary = _get_changes_summary()
        ai_summary = ask_llm(changes_summary)
        commit_message = _build_commit_message(message, stats, ai_summary)
        if not _get_user_confirmation(commit_message):
            return commit_and_push_changes()
        _perform_git_commit(commit_message)
        _push_to_branch()

    except KeyboardInterrupt:
        print('\n', end='')
        print_gradient("👋 Commit cancelled", "yellow_orange")
        sys.exit(0)
