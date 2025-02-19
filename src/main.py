import signal
import subprocess
import sys

from dotenv import load_dotenv

from format import print_gradient
from git import commit_and_push_changes, is_git_repository


def _signal_handler(_signum: int, _frame: object) -> None:
    print('\n', end='')
    print_gradient("👋 Exiting...", "yellow_orange")
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGINT, _signal_handler)
    load_dotenv()

    if is_git_repository() is False:
        print_gradient("❌ Error: Not a git repository", "red_magenta")
        sys.exit(1)

    print_gradient("🚧 Checking for changes...", "yellow_orange")

    subprocess.run(['git', 'add', '.'], check=True)
    status = subprocess.check_output(['git', 'status',
                                      '--porcelain']).decode().strip()

    if status:
        message: str = sys.argv[1] if len(sys.argv) > 1 else ""
        commit_and_push_changes(message)
    else:
        print_gradient("❌ Error: No changes to commit", "red_magenta")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
