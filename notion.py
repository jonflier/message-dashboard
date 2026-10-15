import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_TOKEN'))
database_id = os.getenv('NOTION_DATABASE_ID')

def get_page_content(block_id):
    try:
        blocks = notion.blocks.children.list(block_id=block_id)
        content_lines = []
        for block in blocks.get('results', []):
            block_type = block.get('type')
            value = block.get(block_type, {})
            rich_texts = value.get('rich_text', [])
            text = "".join([rt.get('plain_text', '') for rt in rich_texts])
            if text:
                content_lines.append(text)
        return "\n\n".join(content_lines)
    except Exception as e:
        print(f"Error fetching blocks for page {block_id}: {e}")
        return ""

response = notion.databases.query(database_id=database_id)
print(f"Successfully retrieved {len(response['results'])} entries from Notion.")

entries = []

for page in response['results']:
    page_id = page['id']
    props = page.get('properties', {})
    
    # 1. Extract Title
    title_list = props.get('Name', {}).get('title', [])
    title = title_list[0]['text']['content'] if title_list else "Untitled Entry"
    
    # 2. Extract Due Date
    date_prop = props.get('Due Date', {}).get('date', {})
    date_str = date_prop.get('start') if date_prop else None
    
    if not date_str:
        continue 

    # 3. Extract URL
    url_val = props.get('URL', {}).get('url', '')

    # 4. Fetch Page Content Blocks
    body_content = get_page_content(page_id)
    
    entries.append({
        "title": title,
        "date": date_str,
        "url": url_val,
        "content": body_content
    })

# Write out to notion_export.md
output_filename = "notion_export.md"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("# Notion Export\n\n")
    for entry in entries:
        f.write(f"## {entry['title']}\n")
        if entry['url']:
            f.write(f"**Source:** Notion | **Date:** {entry['date']} | [Original Link]({entry['url']})\n\n")
        else:
            f.write(f"**Source:** Notion | **Date:** {entry['date']}\n\n")
        f.write("---\n\n")
        f.write(f"{entry['content']}\n\n")
        f.write("\n---\n\n")

print("Notion export complete!")