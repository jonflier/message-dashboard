import gspread

# Authorize using your downloaded credentials file
gc = gspread.service_account(filename='credentials.json')

# Open your spreadsheet by its exact title in Google Drive
sheet = gc.open("Quotes and Illustrations Repository").sheet1

# Pull all records as a list of dictionaries
data = sheet.get_all_records()

print(f"Successfully retrieved {len(data)} rows from Google Sheets!")

markdown_output = "# Quotes & Illustrations Repository\n\n"

for idx, row in enumerate(data, start=1):
    quote_text = row.get('Quote', '').strip()
    ill_text = row.get('Illustration', '').strip()
    source = row.get('Source', '').strip()
    category = row.get('Category', '').strip() or 'General'
    
    # Skip completely empty rows
    if not quote_text and not ill_text:
        continue
        
    item_type = "Quote" if quote_text else "Illustration"
    title = f"{category} {item_type} #{idx}"
    
    markdown_output += f"## {title}\n"
    markdown_output += f"**Category**: {category} | **Source**: {source or 'Unknown'}\n\n"
    
    if quote_text:
        markdown_output += f"> \"{quote_text}\"\n\n"
    if ill_text:
        markdown_output += f"{ill_text}\n\n"
        
    markdown_output += "---\n\n"

with open("sheets_export.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)

print("Sheets export updated successfully!")