import pdfplumber

pdf_path = "RegistroCondicionesProduccion_OsmosisInversa.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            print(f"\n--- Page {i+1} ---")
            text = page.extract_text()
            print("TEXT (first 500 chars):")
            print(text[:500] if text else "No text found")
            
            tables = page.extract_tables()
            print(f"\nFound {len(tables)} tables.")
            if tables:
                for j, table in enumerate(tables):
                    print(f"  Table {j+1} rows: {len(table)}")
                    print("  First 3 rows:")
                    for row in table[:3]:
                        print("   ", row)
except Exception as e:
    print("Error:", e)
