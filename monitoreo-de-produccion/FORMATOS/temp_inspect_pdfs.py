import pdfplumber

pdfs = [
    "c:/PROYECTOS/FORMATOS/BitacoraControldeCalidad (Monitoreo).pdf",
    "c:/PROYECTOS/FORMATOS/Bitacora_Suavizador.pdf",
    "c:/PROYECTOS/FORMATOS/RegistroCalidadPozos.pdf"
]

for pdf_path in pdfs:
    print(f"--- {pdf_path} ---")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages[:1]): # Read first page only for layout
                text = page.extract_text(layout=True)
                print(text)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    print("\n\n")
