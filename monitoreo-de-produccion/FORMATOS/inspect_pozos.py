import pdfplumber

pdf_path = "RegistroCalidadPozos.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"--- Page {i+1} ---")
        tables = page.extract_tables()
        if tables:
            for j, table in enumerate(tables):
                print(f"Table {j+1}:")
                for row in table[:10]:
                    print(row)
        else:
            print("No tables found on this page.")
        
        text = page.extract_text()
        if text:
            print("Text Preview:")
            print(text[:800])
