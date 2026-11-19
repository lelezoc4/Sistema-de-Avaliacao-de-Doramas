# -*- coding: utf-8 -*-

from datetime import datetime
from fpdf import FPDF
COLUNAS = ("Data", "Descrição", "Categoria", "Membro", "Valor")
LARGURAS = (24, 66, 40, 25, 35)


def latin1(texto):
   """Troca por '?' os caracteres que a fonte Helvetica não tem (emojis, travessão...)."""
   return texto.encode("latin-1", "replace").decode("latin-1")


def gerar_pdf(caminho, subtitulo, linhas):   
   pdf = FPDF()                        
   pdf.add_page()
   pdf.set_font("Helvetica", "B", 16)
   pdf.cell(0, 10, "Finanças da Família - Relatório de lançamentos", new_x="LMARGIN", new_y="NEXT")
   pdf.set_font("Helvetica", "", 11)
   pdf.cell(0, 7, subtitulo, new_x="LMARGIN", new_y="NEXT")
   pdf.cell(0, 7, f"Emitido em {datetime.now():%d/%m/%Y %H:%M}", new_x="LMARGIN", new_y="NEXT")
   pdf.ln(4)                            # um espaço antes da tabela

   # Tabela. Primeira linha vira o cabeçalho
   pdf.set_font("Helvetica", "", 10)
   with pdf.table(col_widths=LARGURAS, text_align=("LEFT", "LEFT", "LEFT", "LEFT", "RIGHT")) as tabela:
       cabecalho = tabela.row()
       for titulo in COLUNAS:
           cabecalho.cell(titulo)
       for linha in linhas:
           nova = tabela.row()
           for valor in linha:
               nova.cell(latin1(valor))
   pdf.output(caminho)