import pdfplumber
import pandas as pd
import os

pdf_path = "Bitacora_Suavizador.pdf"
excel_path = "Bitacora_Suavizador.xlsx"

def clean_table(table):
    if not table:
        return None
    # Filter out completely empty rows and columns
    df = pd.DataFrame(table)
    df = df.dropna(how='all').dropna(axis=1, how='all')
    return df

with pdfplumber.open(pdf_path) as pdf:
    all_tables = []
    
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            df = clean_table(table)
            if df is not None and not df.empty:
                all_tables.append((f"Page_{i+1}_Table_{j+1}", df))

# Write to Excel
if all_tables:
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        row_offset = 0
        workbook = writer.book
        worksheet = workbook.create_sheet('Bitacora_Suavizador')
        writer.sheets['Bitacora_Suavizador'] = worksheet
        
        for name, df in all_tables:
            # write title
            worksheet.cell(row=row_offset+1, column=1, value=name)
            
            # write dataframe
            df.to_excel(writer, sheet_name='Bitacora_Suavizador', startrow=row_offset+1, index=False, header=False)
            row_offset += len(df) + 3
            
        # Remove default empty sheet
        if 'Sheet' in workbook.sheetnames:
            workbook.remove(workbook['Sheet'])
            
    print(f"Successfully converted {len(all_tables)} tables to {excel_path}")
else:
    print("No tables found in the PDF.")
