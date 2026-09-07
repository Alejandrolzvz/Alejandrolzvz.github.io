import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

def create_fillable_form(filename="Registro_Osmosis_Inversa_Digital.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registro Osmosis"

    # Styles
    bold_font = Font(bold=True, size=12)
    header_font = Font(bold=True, size=14)
    normal_font = Font(size=11)
    
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    right_align = Alignment(horizontal="right", vertical="center", wrap_text=True)
    
    thin_border = Border(left=Side(style='thin'), 
                         right=Side(style='thin'), 
                         top=Side(style='thin'), 
                         bottom=Side(style='thin'))
                         
    fill_bg = PatternFill(start_color="E0F2F1", end_color="E0F2F1", fill_type="solid") # Light greenish blue for input fields
    title_bg = PatternFill(start_color="B0BEC5", end_color="B0BEC5", fill_type="solid") # Light gray for headers
    
    # Configure Column Widths
    ws.column_dimensions['A'].width = 30
    for col in ['B', 'C', 'D', 'E', 'F', 'G']:
        ws.column_dimensions[col].width = 15

    # Headers
    ws.merge_cells('A1:E1')
    ws['A1'] = "3 Monitoreo de Osmosis Inversa"
    ws['A1'].font = header_font
    ws['A1'].alignment = center_align

    ws['A2'] = "Planta:"
    ws['A2'].font = bold_font
    ws['B2'].fill = fill_bg
    ws['B2'].border = thin_border
    
    ws['D2'] = "Fecha:"
    ws['D2'].font = bold_font
    ws['E2'].fill = fill_bg
    ws['E2'].border = thin_border

    ws.merge_cells('A3:E3')
    ws['A3'] = "Registro de condiciones de producción de agua purificada"
    ws['A3'].font = bold_font
    ws['A3'].alignment = center_align

    ws.merge_cells('A4:E4')
    ws['A4'] = "SACPST-RA-05"
    ws['A4'].font = bold_font
    ws['A4'].alignment = right_align

    # Table 1: Monitoreo
    ws['A6'] = "HORA DE MONITOREO"
    ws['A6'].font = bold_font
    ws['A6'].fill = title_bg
    ws['A6'].border = thin_border
    
    times = ["6:00 A.M.", "8:00 A.M.", "10:00 A.M.", "12:00 P.M."]
    for col_idx, time in enumerate(times, start=2):
        cell = ws.cell(row=6, column=col_idx, value=time)
        cell.font = bold_font
        cell.alignment = center_align
        cell.fill = title_bg
        cell.border = thin_border

    ws['A7'] = "Indique Estatus:\n(Encendido o Apagado)"
    ws['A7'].font = bold_font
    ws['A7'].alignment = center_align
    ws['A7'].border = thin_border
    for col_idx in range(2, 6):
        cell = ws.cell(row=7, column=col_idx)
        cell.fill = fill_bg
        cell.border = thin_border

    # Section Helper
    def add_section(start_row, title, parameters):
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=5)
        ws.cell(row=start_row, column=1, value=title).font = bold_font
        ws.cell(row=start_row, column=1).fill = title_bg
        ws.cell(row=start_row, column=1).border = thin_border
        
        current_row = start_row + 1
        for param in parameters:
            # Parameter Name
            c1 = ws.cell(row=current_row, column=1, value=param)
            c1.font = normal_font
            c1.border = thin_border
            # Input fields
            for col_idx in range(2, 6):
                c = ws.cell(row=current_row, column=col_idx)
                c.fill = fill_bg
                c.border = thin_border
            current_row += 1
        return current_row

    row = 9
    row = add_section(row, "Presiones (Psi)", [
        "De Arranque (80-100)",
        "De Agua Cruda (40-50)",
        "Pre Filtración (20-30)",
        "Post Filtración (20-30)",
        "Pre Membranas (140-50)",
        "Post Membranas (90-100)",
        "De Bombas (150)"
    ])

    row += 1
    row = add_section(row, "Rotámetros (gpm)", [
        "De Productos (80-90)",
        "De Rechazo (18-20)"
    ])

    row += 1
    row = add_section(row, "Sensores", [
        "pH (6.5-7.0)",
        "S.T.D. (40-60ppm) (Antes de la mezcla)"
    ])

    row += 1
    row = add_section(row, "Lectores", [
        "Amperimetro (40)",
        "Horometro"
    ])

    row += 1
    row = add_section(row, "Presión en Filtros (Psi)", [
        "Arena (60-80)",
        "Carbón (50-60)",
        "Suavizador 1 o 2",
        "Entrada de Suavizador (50-70)",
        "Salida de Suavizador (45-55)"
    ])

    row += 2
    # Second part of the form
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
    ws.cell(row=row, column=2, value="6:00 A.M. a 10:00 A.M.").alignment = center_align
    ws.cell(row=row, column=2).font = bold_font
    
    ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=5)
    ws.cell(row=row, column=4, value="11:00 A.M. a 3:00 P.M.").alignment = center_align
    ws.cell(row=row, column=4).font = bold_font
    
    ws.merge_cells(start_row=row, start_column=6, end_row=row, end_column=7)
    ws.cell(row=row, column=6, value="4:00 P.M. a 8:00 P.M.").alignment = center_align
    ws.cell(row=row, column=6).font = bold_font
    
    row += 1
    headers2 = ["S.T.D. (ppm)", "Eficiencia %", "Rango %", "Eficiencia %", "Rango %", "Eficiencia %", "Rango %"]
    for col_idx, h in enumerate(headers2, start=1):
        c = ws.cell(row=row, column=col_idx, value=h)
        c.font = bold_font
        c.fill = title_bg
        c.border = thin_border
        
    row += 1
    vasos = ["Vaso 1 (100-90)", "Vaso 2 (100-90)", "Vaso 3 (100-90)", "Vaso 4 (100-90)", "Vaso 5 (100-90)", "Final (100-90)", "Rechazo vasos 1 y 2", "Rechazo Vaso 3", "Rechazo Vaso 4", "Rechazo Vaso 5"]
    for vaso in vasos:
        c1 = ws.cell(row=row, column=1, value=vaso)
        c1.border = thin_border
        for col_idx in range(2, 8):
            c = ws.cell(row=row, column=col_idx)
            c.fill = fill_bg
            c.border = thin_border
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="Entrada de Osmosis").font = bold_font
    
    c1 = ws.cell(row=row, column=2, value="SDT:")
    c1.font = bold_font; c1.alignment = right_align
    ws.cell(row=row, column=3).fill = fill_bg; ws.cell(row=row, column=3).border = thin_border
    
    c2 = ws.cell(row=row, column=4, value="DT:")
    c2.font = bold_font; c2.alignment = right_align
    ws.cell(row=row, column=5).fill = fill_bg; ws.cell(row=row, column=5).border = thin_border

    row += 2
    ws.cell(row=row, column=1, value="Observaciones:").font = bold_font
    ws.merge_cells(start_row=row, start_column=2, end_row=row+2, end_column=7)
    obs_cell = ws.cell(row=row, column=2)
    obs_cell.fill = fill_bg
    obs_cell.border = thin_border
    
    row += 4
    ws.cell(row=row, column=1, value="Nombre y Firma").font = bold_font
    row += 1
    firmas = ["Jefe de 1er Turno", "Jefe de 2do Turno", "Sub Jefe de Producción y Calidad", "Jefe de Producción y Calidad"]
    for idx, f in enumerate(firmas):
        ws.cell(row=row, column=idx*2+1, value=f).alignment = center_align
        ws.merge_cells(start_row=row, start_column=idx*2+1, end_row=row, end_column=idx*2+2)
        # Signature line
        ws.merge_cells(start_row=row-1, start_column=idx*2+1, end_row=row-1, end_column=idx*2+2)
        ws.cell(row=row-1, column=idx*2+1).border = Border(bottom=Side(style='thin'))

    # Protection
    # By default, all cells are protected. We unlock the fillable ones.
    for r in ws.iter_rows():
        for cell in r:
            if cell.fill == fill_bg:
                cell.protection = openpyxl.styles.Protection(locked=False)
                
    ws.protection.enable()

    wb.save(filename)
    print(f"Form created successfully as {filename}")

if __name__ == "__main__":
    create_fillable_form()
