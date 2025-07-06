import subprocess
import os

def get_changed_files():
    """Return list of changed markdown files under posts/ directory."""
    try:
        output = subprocess.check_output(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD']
        ).decode('utf-8')
        changed_files = output.strip().split('\n')
        return [f for f in changed_files if f.startswith('posts/') and f.endswith('.md')]
    except subprocess.CalledProcessError as e:
        print("Error getting changed files:", e)
        return []

if __name__ == "__main__":
    files = get_changed_files()
    print("Changed files:", files)
