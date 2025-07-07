import subprocess
import os
import yaml


import json

import requests

HASHNODE_API_URL = "https://gql.hashnode.com/"

def publish_new_post(title, content, tags, token, publication_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }

    # Step 1: Create Draft
    create_draft_query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        id
      }
    }
    """

    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content,
            "tags": tags,
            "publicationId": publication_id
        }
    }

    response = requests.post(HASHNODE_API_URL, headers=headers, json={
        "query": create_draft_query,
        "variables": variables
    })

    result = response.json()
    if 'errors' in result:
        print("❌ Failed to create draft:", result['errors'])
        return None

    draft_id = result['data']['createDraft']['id']
    print("📝 Draft created:", draft_id)

    # Step 2: Publish the Draft
    publish_query = """
    mutation PublishDraft($id: ID!) {
      publishDraft(id: $id) {
        post {
          id
        }
      }
    }
    """

    publish_response = requests.post(HASHNODE_API_URL, headers=headers, json={
        "query": publish_query,
        "variables": {
            "id": draft_id
        }
    })

    publish_result = publish_response.json()
    if 'errors' in publish_result:
        print("❌ Failed to publish draft:", publish_result['errors'])
        return None

    post_id = publish_result['data']['publishDraft']['post']['id']
    print("✅ Post published with ID:", post_id)
    return post_id


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
    HASHNODE_TOKEN = "0279e873-a85d-4ed0-9938-ef88021c92b9"
    PUBLICATION_ID = "68698ae9adb6b7f95bf6d40f"

    files = get_changed_files()
    mapping = load_mapping()

    for f in files:
        blog_data = parse_markdown(f)
        post_id = mapping.get(f)

        print(f"\n📝 Processing: {f}")
        print("→ Title:", blog_data['title'])
        print("→ Tags:", blog_data['tags'])

        if post_id:
            print("🟡 Post already exists → will update (we’ll do that in the next step)")
            continue  # We'll handle updating in the next step
        else:
            print("🟢 New post → publishing to Hashnode...")

            # Call publish function
            new_post_id = publish_new_post(
    title=blog_data['title'],
    content=blog_data['content'],
    tags=blog_data['tags'],
    token=HASHNODE_TOKEN,
    publication_id=PUBLICATION_ID
)


            # Save post ID
            if new_post_id:
                mapping[f] = new_post_id
                save_mapping(mapping)
                print("✅ Post ID saved to mapping.")
            else:
                print("❌ Failed to publish.")
