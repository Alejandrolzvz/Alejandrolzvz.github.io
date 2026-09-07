import pdfplumber

pdf_path = "BitacoraControldeCalidad (Monitoreo).pdf"

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"--- Page {i+1} ---")
        tables = page.extract_tables()
        if tables:
            for j, table in enumerate(tables):
                print(f"Table {j+1}:")
                for row in table[:8]: # Show first 8 rows for more context
                    print(row)
        else:
            print("No tables found on this page.")
        
        text = page.extract_text()
        if text:
            print("Text Preview:")
            print(text[:800])
        
        # Stop after 3 pages if it's long, usually these are repetitive
        if i >= 2:
            break
