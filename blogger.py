from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import re

SCOPES = ['https://www.googleapis.com/auth/blogger.readonly']
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES
)

service = build('blogger', 'v3', credentials=creds)

BLOG_ID = "1655599457547601718"

def clean_unicode_artifacts(text):
    return re.sub(r'[\u200e\u200f\u202a-\u202e]', '', text)

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Preserve bold and italics by swapping them for Markdown syntax before stripping tags
    for b in soup.find_all(['b', 'strong']):
        b.replace_with(f"**{b.get_text()}**")
    for i in soup.find_all(['i', 'em']):
        i.replace_with(f"*{i.get_text()}*")
        
    # Convert line breaks into spacing
    for br in soup.find_all('br'):
        br.replace_with('\n')
        
    # Extract text block-by-block so sentences don't shatter mid-line
    blocks = []
    for element in soup.find_all(['p', 'div', 'blockquote', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        block_text = element.get_text(separator=' ')
        cleaned_block = ' '.join(block_text.split())
        if cleaned_block:
            blocks.append(cleaned_block)
            
    if not blocks:
        fallback_text = ' '.join(soup.get_text(separator=' ').split())
        return clean_unicode_artifacts(fallback_text)

    return clean_unicode_artifacts('\n\n'.join(blocks))

def fetch_blog_posts():
    try:
        output_filename = "blogger_export.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("# Blogger Posts Export\n\n")
            
            page_token = None
            total_posts = 0
            
            while True:
                response = service.posts().list(
                    blogId=BLOG_ID, 
                    maxResults=50, 
                    pageToken=page_token
                ).execute()
                
                posts = response.get('items', [])
                if not posts:
                    break
                    
                for post in posts:
                    title = post.get('title', 'Untitled')
                    url = post.get('url', '')
                    raw_content = post.get('content', '')
                    published = post.get('published', '')[:10]
                    
                    clean_content = clean_html(raw_content)
                    
                    f.write(f"## {title}\n")
                    f.write(f"**Published:** {published} | **[Read Online]({url})**\n\n")
                    f.write("---\n\n")
                    f.write(f"{clean_content}\n\n")
                    f.write("\n---\n\n")
                    total_posts += 1
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
                
        print(f"Blogger export complete! Fetched {total_posts} posts to '{output_filename}'.")
        
    except Exception as e:
        print(f"Error fetching Blogger posts: {e}")

if __name__ == "__main__":
    fetch_blog_posts()