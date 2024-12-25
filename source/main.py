import subprocess
import signal
import sys
import os

from dotenv import load_dotenv
from mistralai import Mistral


def gradient_text(text, start_hex, end_hex, bold=True):
    result = ""
    start_hex = start_hex.lstrip('#')
    end_hex = end_hex.lstrip('#')
    
    start_r, start_g, start_b = (int(start_hex[i:i+2], 16) for i in (0, 2, 4))
    end_r, end_g, end_b = (int(end_hex[i:i+2], 16) for i in (0, 2, 4))
    
    for i, char in enumerate(text):
        progress = i / (len(text) - 1) if len(text) > 1 else 0
        r = int(start_r + (end_r - start_r) * progress)
        g = int(start_g + (end_g - start_g) * progress)
        b = int(start_b + (end_b - start_b) * progress)
        result += f"\033[{('1;' if bold else '')}38;2;{r};{g};{b}m{char}"
    
    return result + "\033[0m"


def print_gradient(text, type="light_gray", line_break=True):
    colors = {
        "red_magenta": ("#FF2828", "#FF28FF"),
        "cyan_blue": ("#28FFFF", "#2828FF"),
        "green_lime": ("#28FF28", "#28FFB4"),
        "yellow_orange": ("#FFFF28", "#FFB428"),
        "light_gray": ("#FAFAFA", "#E1EAEE"),
        "pink_purple": ("#FF28FF", "#B428FF")
    }
    
    start_hex, end_hex = colors.get(type, colors["light_gray"])
    print(gradient_text(text, start_hex, end_hex,
                        bold=(type != "light_gray")),
          end='\n' if line_break else '')

def box_print(text):
    lines = text.split('\n')
    width = max(len(line) for line in lines)
    
    box = f"╭{'─' * (width + 2)}╮\n"
    for line in lines:
        box += f"│ {line:<{width}} │\n"
    box += f"╰{'─' * (width + 2)}╯"
    return box


def is_git_repository():
    try:
        subprocess.check_output(['git', 'rev-parse', '--git-dir'],
                                stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def get_changed_files(filter_type):
    result = subprocess.check_output(['git', 'diff', '--cached',
                                      '--name-only',
                                      f'--diff-filter={filter_type}'])
    return ["      " + line for line in result.decode().splitlines()]


def is_initial_commit():
    try:
        subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                stderr=subprocess.DEVNULL)
        return False
    except subprocess.CalledProcessError:
        return True


def get_changes_summary():
    try:
        if is_initial_commit():
            result = subprocess.check_output(['git', 'diff', '--cached'])
        else:
            result = subprocess.check_output(['git', 'diff', 'HEAD'])
        return '\n'.join(['\t' + line for line in result.decode().splitlines()])
    except subprocess.CalledProcessError as e:
        print_gradient(f"❌ Error: could not get changes summary: {str(e)}",
                       "red_magenta")
        sys.exit(1)


def request_ai(prompt):
    system_prompt_path = '/home/maty/Tools/ai-git-push/config/sys_prompt.md'
    if not os.path.isfile(system_prompt_path):
        system_prompt_path = '/Users/maty/Tools/ai-git-push/config/sys_prompt.md'
        if not os.path.isfile(system_prompt_path):
            print_gradient("❌ Error: 'sys_prompt.md' file not found.",
                           "red_magenta")
            sys.exit(1)
    with open(system_prompt_path, 'r') as f:
        system_prompt = f.read()

    api_key = os.getenv('MISTRAL_API_KEY')
    client = Mistral(api_key)

    print_gradient("💭 AI generating commit message...", "cyan_blue")

    try:
        stream = client.chat.complete(
            model=os.getenv('MISTRAL_MODEL'),
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
            ]
        )
        return stream.choices[0].message.content
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def generate_commit_message(message=None):
    try:
        added_files = get_changed_files('A')
        modified_files = get_changed_files('M')
        deleted_files = get_changed_files('D')
        renamed_files = get_changed_files('R')

        changes_summary = get_changes_summary()

        ai_summary = request_ai(changes_summary)

        added_count = len(added_files)
        modified_count = len(modified_files)
        deleted_count = len(deleted_files)
        renamed_count = len(renamed_files)

        if message:
            commit_message = message
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

        with open('commit_msg.txt', 'w') as f:
            f.write(commit_message)

        subprocess.run(['git', 'commit', '-F', 'commit_msg.txt'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove('commit_msg.txt')

        branch = subprocess.check_output([
            'git', 'branch', '--show-current']).decode().strip()
        print_gradient(f"🚀 Pushing to {branch}...", "cyan_blue")
        push_result = subprocess.run(['git', 'push', 'origin', branch],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
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


def signal_handler(sig, frame):
    print('\n', end='')
    print_gradient("👋 Exiting...", "yellow_orange")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    load_dotenv()

    try:
        if not is_git_repository():
            print_gradient("❌ Error: Not a git repository", "red_magenta")
            sys.exit(1)

        print_gradient("🚧 Checking for changes...", "yellow_orange")
        subprocess.run(['git', 'add', '.'])

        status = subprocess.check_output([
            'git', 'status', '--porcelain']).decode().strip()
        if status:
            message = sys.argv[1] if len(sys.argv) > 1 else None
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
