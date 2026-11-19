# -*- coding: utf-8 -*-

from conexao import conectar

SQL_LISTAR = """
   SELECT a.id, a.data, a.nota, a.descricao, a.dorama_id, a.usuario_id
   FROM Avaliacao a
   JOIN Dorama d ON d.id = a.dorama_id
   JOIN Usuario u ON u.id = a.usuario_id
"""

def listar():
    """ READ """
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(SQL_LISTAR + " ORDER BY a.data, a.id")
        return cursor.fetchall()

def buscar(id_avaliacao):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT data, descricao, nota, usuario_id, dorama_id "
                       "FROM Avaliacao WHERE id = %s", (id_avaliacao,))
        return cursor.fetchone()

def inserir(data, descricao, nota, usuario_id, dorama_id):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO Avaliacao (data, descricao, nota, usuario_id, dorama_id) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (data, descricao, nota, usuario_id, dorama_id))
        conexao.commit()

def atualizar(id_avaliacao, data, descricao, nota, usuario_id, dorama_id):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("UPDATE Avaliacao SET data = %s, descricao = %s, nota = %s, "
                       "usuario_id = %s, dorama_id = %s WHERE id = %s",
                       (data, descricao, nota, usuario_id, dorama_id, id_avaliacao))
        conexao.commit()

def excluir(id_avaliacao):
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM Avaliacao WHERE id = %s", (id_avaliacao,))
        conexao.commit()