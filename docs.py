from google.oauth2 import service_account
from googleapiclient.discovery import build
import re

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES
)

service = build('docs', 'v1', credentials=creds)

DOCUMENTS_TO_PULL = [
    {"name": "Messages & Drafts", "id": "1EEqRi20vfmEI-BEYPE_od6ojGeY9k3qQWKy9qohDMJg", "filename": "docs_export.md"},
    {"name": "Notes & Miscellaneous", "id": "1hF4nceY0xFEcU9Fi0HB3roBytg17cZ5hGdea8foKyWs", "filename": "notes_export.md"}
]

def clean_unicode_artifacts(text):
    return re.sub(r'[\u200e\u200f\u202a-\u202e]', '', text)

def parse_table(table_element):
    markdown_lines = []
    table = table_element.get('table', {})
    
    for row in table.get('tableRows', []):
        row_texts = []
        for cell in row.get('tableCells', []):
            cell_content = cell.get('content', [])
            cell_text = extract_text_from_elements(cell_content).strip().replace('\n', ' ')
            row_texts.append(cell_text)
            
        if len(row_texts) >= 2:
            if not row_texts[1].strip():
                markdown_lines.append(f"| {row_texts[0]} |")
            else:
                markdown_lines.append(f"| {row_texts[0]} | {row_texts[1]} |")
        elif len(row_texts) == 1:
            markdown_lines.append(f"| {row_texts[0]} |")
            
    return "\n" + "\n".join(markdown_lines) + "\n"

def extract_text_from_elements(elements):
    text = ''
    for value in elements:
        if 'paragraph' in value:
            for elem in value.get('paragraph').get('elements', []):
                text_run = elem.get('textRun')
                if text_run:
                    text += text_run.get('content')
        elif 'table' in value:
            text += parse_table(value)
        elif 'tableOfContents' in value:
            toc = value.get('tableOfContents', {})
            text += extract_text_from_elements(toc.get('content', []))
            
    return clean_unicode_artifacts(text)

def process_tab(tab, f):
    tab_props = tab.get('tabProperties', {})
    fallback_title = tab_props.get('title', 'Untitled Note')
    clean_title = fallback_title.strip().lower()
    
    is_master_container = ('messages' in clean_title or 'template' in clean_title or 'overview' in clean_title)

    if not is_master_container:
        body_content = tab.get('documentTab', {}).get('body', {}).get('content', [])
        tab_text = extract_text_from_elements(body_content).strip()
        
        if tab_text:
            lines = tab_text.split('\n')
            sermon_title = ""
            date_str = ""
            cleaned_lines = lines  
            
            first_line = ""
            for line in lines:
                if line.strip():
                    first_line = line.strip()
                    break

            if '@' in first_line:
                parts = first_line.split('@')
                potential_title = parts[0].strip()
                remainder = parts[1].strip()
                
                if potential_title and potential_title.lower() != "title":
                    sermon_title = potential_title
                    
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})|(\d{2}\.\d{2}\.\d{2})|(\d{4}-\d{2}-\d{2})', remainder)
                if date_match:
                    date_str = date_match.group(0)
            else:
                if first_line and len(first_line) < 80:
                    sermon_title = first_line
                else:
                    sermon_title = fallback_title

            if not sermon_title or sermon_title.lower() == "title":
                sermon_title = fallback_title

            if not date_str:
                date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{2,4})|(\d{2}\.\d{2}\.\d{2})|(\d{4}-\d{2}-\d{2})', fallback_title)
                if date_match:
                    date_str = date_match.group(0)

            body_markdown = "\n".join(cleaned_lines).strip()

            if date_str:
                f.write(f"## {sermon_title}\n")
                f.write(f"**Source:** Google Doc | **Date:** {date_str}\n\n")
            else:
                f.write(f"## {sermon_title}\n")
                f.write(f"**Source:** Google Doc\n\n")
                
            f.write("---\n\n")
            f.write(f"{body_markdown}\n\n")
            f.write("\n---\n\n")

    for child in tab.get('childTabs', []):
        process_tab(child, f)

for doc_info in DOCUMENTS_TO_PULL:
    output_filename = doc_info["filename"]
    try:
        print(f"Pulling {doc_info['name']} -> {output_filename}...")
        document = service.documents().get(documentId=doc_info["id"], includeTabsContent=True).execute()
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"# {doc_info['name']}\n\n")
            for tab in document.get('tabs', []):
                process_tab(tab, f)
        print(f"Successfully exported {doc_info['name']}!")
    except Exception as e:
        print(f"Error loading {doc_info['name']}: {e}")

print("All Docs exports complete!")