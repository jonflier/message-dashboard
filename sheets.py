import gspread

gc = gspread.service_account(filename='credentials.json')
spreadsheet = gc.open("Quotes and Illustrations Repository")
sheet = spreadsheet.sheet1
rows = sheet.get_all_values()

if not rows:
    print("Spreadsheet is empty!")
    exit()

markdown_output = "# Quotes & Illustrations Repository\n\n"

item_counter = 1
for row in rows[1:]:
    while len(row) < 5:
        row.append('')
        
    quote_text = row[1].strip()             # Column B: Quote
    ill_text = row[2].strip()               # Column C: Illustration
    source = row[3].strip()                 # Column D: Source
    category = row[4].strip() or 'General'  # Column E: Category
    
    if not quote_text and not ill_text:
        continue
        
    item_type = "Quote" if quote_text and not ill_text else ("Illustration" if ill_text and not quote_text else "Entry")
    title = f"{item_type} #{item_counter}"
    
    markdown_output += f"## {title}\n"
    markdown_output += "---\n\n"
    
    # Place the quote or illustration text first
    if quote_text:
        formatted_quote = quote_text.replace('\n', '\n> ')
        markdown_output += f"> \"{formatted_quote}\"\n\n"
        
    if ill_text:
        markdown_output += f"{ill_text}\n\n"
        
    # Append the source at the bottom of the body text so the frontend renders it reliably
    if source:
        markdown_output += f"\n\n**Source:** {source}\n"
        
    markdown_output += "\n---\n\n"
    item_counter += 1

with open("sheets_export.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)

print(f"Successfully exported {item_counter - 1} rows to sheets_export.md!")