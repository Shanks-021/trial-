import subprocess
import os
import yaml


import json

# Load the JSON mapping file
def load_mapping(mapping_path='hashnode-mapping.json'):
    if not os.path.exists(mapping_path):
        return {}
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save updated mapping
def save_mapping(mapping, mapping_path='hashnode-mapping.json'):
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)


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
    

def parse_markdown(filepath):
    """Extract frontmatter (title, tags) and content from a Markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by frontmatter block
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return {
                'title': front_matter.get('title'),
                'tags': front_matter.get('tags', []),
                'content': body
            }

    # If no frontmatter
    return {
        'title': None,
        'tags': [],
        'content': content.strip()
    }

# Example usage

if __name__ == "__main__":
    files = get_changed_files()
    mapping = load_mapping()

    for f in files:
        blog_data = parse_markdown(f)
        post_id = mapping.get(f)

        print(f"\nParsed: {f}")
        print("Title:", blog_data['title'])
        print("Tags:", blog_data['tags'])
        print("Content Preview:", blog_data['content'][:100])

        if post_id:
            print("🟡 This post already exists on Hashnode (Post ID:", post_id, ") → Will update")
        else:
            print("🟢 New post → Will publish to Hashnode and save post ID")





