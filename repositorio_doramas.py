# -*- coding: utf-8 -*-

from conexao import conectar

def listar():
    """READ: retorna os doramas por ordem alfabética do título."""
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT id, titulo, genero, plataforma, qtd_capitulos FROM Dorama ORDER BY titulo")
        return cursor.fetchall()

def inserir(titulo, genero, plataforma, qtd_capitulos):
   """CREATE: grava um novo dorama."""
   with conectar() as conexao:
       cursor = conexao.cursor()
       cursor.execute("INSERT INTO Dorama (titulo, genero, plataforma, qtd_capitulos) VALUES (%s, %s, %s, %s)", (titulo, genero, plataforma, qtd_capitulos))
       conexao.commit()

def atualizar(id_dorama, titulo, genero, plataforma, qtd_capitulos):
   """UPDATE: altera o título, gênero, plataforma e quantidade de capítulos do dorama com esse id."""
   with conectar() as conexao:
       cursor = conexao.cursor()
       cursor.execute("UPDATE Dorama SET titulo = %s, genero = %s, plataforma = %s, qtd_capitulos = %s WHERE id = %s", (titulo, genero, plataforma, qtd_capitulos, id_dorama))
       conexao.commit()

def excluir(id_dorama):
   """DELETE: apaga o dorama com esse id."""
   with conectar() as conexao:
       cursor = conexao.cursor()
       cursor.execute("DELETE FROM Dorama WHERE id = %s", (id_dorama,))
       conexao.commit()