"""
Main module for the AI Git Push tool.
"""

import signal
import subprocess
import sys

from dotenv import load_dotenv
from format import print_gradient
from git import commit_and_push_changes, is_git_repository


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
            commit_and_push_changes(message)
        else:
            print_gradient("❌ Error: No changes to commit", "red_magenta")
            sys.exit(1)
    except KeyboardInterrupt:
        print('\n', end='')
        print_gradient("👋 Operation cancelled", "yellow_orange")
        sys.exit(0)


if __name__ == "__main__":
    main()
