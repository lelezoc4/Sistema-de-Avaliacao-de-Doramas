# -*- coding: utf-8 -*-

"""Testa o relatório pelo terminal, com duas linhas inventadas."""
import relatorio
linhas = [
   ("03/09/2026", "Supermercado", "Mercado", "Jorge", "- R$ 412,35"),
   ("05/09/2026", "Salário de setembro", "Salário", "Marta", "+ R$ 3.200,00"),
]
relatorio.gerar_pdf("teste.pdf", "Período: 01/09/2026 a 30/09/2026", linhas)
print("PDF gerado: teste.pdf")