"""
Main module for the AI Git Push tool.
"""

import os
import signal
import subprocess
import sys

from dotenv import load_dotenv
from format import box_print, print_gradient
from git import get_changed_files, get_changes_summary, is_git_repository
from llm import ask_llm


def generate_commit_message(message: str = "") -> None:
    """
    Generate a commit message and push to the current branch.
    """
    try:
        added_files = get_changed_files('A')
        modified_files = get_changed_files('M')
        deleted_files = get_changed_files('D')
        renamed_files = get_changed_files('R')

        changes_summary = get_changes_summary()

        ai_summary = ask_llm(changes_summary)

        added_count = len(added_files)
        modified_count = len(modified_files)
        deleted_count = len(deleted_files)
        renamed_count = len(renamed_files)

        if message:
            commit_message: str = message
        else:
            commit_message = f"{ai_summary}\n\nDetailed changes:"
            if added_count > 0:
                commit_message += (f"\n\nAdded ({added_count}):\n"
                                   + '\n'.join(added_files))
            if modified_count > 0:
                commit_message += (f"\n\nModified ({modified_count}):\n"
                                   + '\n'.join(modified_files))
            if deleted_count > 0:
                commit_message += (f"\n\nDeleted ({deleted_count}):\n"
                                   + '\n'.join(deleted_files))
            if renamed_count > 0:
                commit_message += (f"\n\nRenamed ({renamed_count}):\n"
                                   + '\n'.join(renamed_files))

        print_gradient("✅ Successfully generated commit message", "green_lime")
        print_gradient(box_print(commit_message), "light_gray")
        print_gradient("🛎️ Do you want to proceed? [Y/n] ", "yellow_orange",
                       False)
        response = input()
        if response.lower() not in ('y', 'yes', ''):
            return generate_commit_message()

        with open('commit_msg.txt', 'w', encoding='utf-8') as f:
            f.write(commit_message)

        subprocess.run(['git', 'commit', '-F', 'commit_msg.txt'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True)
        os.remove('commit_msg.txt')

        branch = subprocess.check_output([
            'git', 'branch', '--show-current']).decode().strip()
        print_gradient(f"🚀 Pushing to {branch}...", "cyan_blue")
        push_result = subprocess.run(['git', 'push', 'origin', branch],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL,
                                     check=False)
        if push_result.returncode == 0:
            print_gradient(f"✅ Successfully pushed to {branch}",
                           "green_lime")
        else:
            print_gradient(f"❌ Error: Failed to push to {branch}",
                           "red_magenta")
            print_gradient(f"💡 Try running: git push origin {branch} manually",
                           "yellow_orange")
    except KeyboardInterrupt:
        print('\n', end='')
        print_gradient("👋 Commit cancelled", "yellow_orange")
        sys.exit(0)


def signal_handler(_signum: int, _frame: object) -> None:
    """
    Handle the SIGINT signal (Ctrl+C).
    """
    print('\n', end='')
    print_gradient("👋 Exiting...", "yellow_orange")
    sys.exit(0)


def main() -> None:
    """
    Main function.
    """
    signal.signal(signal.SIGINT, signal_handler)
    load_dotenv()

    try:
        if not is_git_repository():
            print_gradient("❌ Error: Not a git repository", "red_magenta")
            sys.exit(1)

        print_gradient("🚧 Checking for changes...", "yellow_orange")
        subprocess.run(['git', 'add', '.'], check=True)

        status = subprocess.check_output([
            'git', 'status', '--porcelain']).decode().strip()
        if status:
            message: str = sys.argv[1] if len(sys.argv) > 1 else ""
            generate_commit_message(message)
        else:
            print_gradient("❌ Error: No changes to commit", "red_magenta")
            sys.exit(1)
    except KeyboardInterrupt:
        print('\n', end='')
        print_gradient("👋 Operation cancelled", "yellow_orange")
        sys.exit(0)


if __name__ == "__main__":
    main()
