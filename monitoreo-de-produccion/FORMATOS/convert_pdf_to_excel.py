import pdfplumber
import pandas as pd

pdf_path = "RegistroCondicionesProduccion_OsmosisInversa.pdf"
excel_path = "RegistroCondicionesProduccion_OsmosisInversa.xlsx"

with pdfplumber.open(pdf_path) as pdf:
    # We will collect all tables into a list of DataFrames
    all_tables = []
    
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            # Convert table to DataFrame
            df = pd.DataFrame(table)
            all_tables.append((f"Page_{i+1}_Table_{j+1}", df))

# Write to Excel
if all_tables:
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # If there are > 0 tables, let's put them all in one sheet with some spacing,
        # or separate sheets if too many. Let's do one sheet for simplicity.
        row_offset = 0
        workbook = writer.book
        worksheet = workbook.create_sheet('Extracted_Tables')
        writer.sheets['Extracted_Tables'] = worksheet
        
        for name, df in all_tables:
            # write title
            worksheet.cell(row=row_offset+1, column=1, value=name)
            
            # write dataframe
            df.to_excel(writer, sheet_name='Extracted_Tables', startrow=row_offset+1, index=False, header=False)
            row_offset += len(df) + 3
            
        # Remove default empty sheet
        if 'Sheet' in workbook.sheetnames:
            workbook.remove(workbook['Sheet'])
            
    print(f"Successfully converted {len(all_tables)} tables to {excel_path}")
else:
    print("No tables found in the PDF.")
