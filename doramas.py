#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cadastro de doramas (CRUD) do projeto de Avaliação de Doramas"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import mysql.connector
import repositorio_doramas as repo

class Aplicacao:
    def __init__(self):
        # construtor
        builder = Gtk.Builder()
        builder.add_from_file("doramas.glade")
        
        self.janela = builder.get_object("janela")
        self.txt_dorama = builder.get_object("txt_dorama")
        self.txt_genero = builder.get_object("txt_genero")
        self.txt_capitulo = builder.get_object("txt_capitulo")
        self.txt_plataforma = builder.get_object("txt_plataforma")
        self.txt_data = builder.get_object("txt_data")
        self.txt_avaliacao = builder.get_object("txt_avaliacao")

        self.btn_gravar = builder.get_object("btn_gravar")
        self.btn_gravar.connect("clicked", self.ao_gravar)
        self.btn_editar = builder.get_object("btn_editar")
        self.btn_editar.connect("clicked", self.ao_editar)
        self.btn_excluir = builder.get_object("btn_excluir")
        self.btn_excluir.connect("clicked", self.ao_excluir)
        self.lbl_mensagem = builder.get_object("lbl_mensagem")
        
        self.tvw_categorias = builder.get_object("tvw_doramas")
        self.lst_categorias = builder.get_object("lst_doramas")
        self.selecao = self.tvw_categorias.get_selection()
        self.selecao.connect("changed", self.ao_mudar_selecao)

        self.id_em_edicao = None

        self.janela.connect("destroy", Gtk.main_quit)
        self.carregar_tabela()
        self.janela.show_all()

    def mostrar_mensagem(self, texto):
       self.lbl_mensagem.set_text(texto)
 
    def carregar_tabela(self):
        """READ"""
        self.lst_categorias.clear()
        try:
            for id_dorama, titulo, genero, capitulo, plataforma, data, avaliacao in repo.listar():
                self.lst_categorias.append([id_dorama, titulo, genero, capitulo, plataforma, data, avaliacao])
        except mysql.connector.Error as erro:
            self.mostrar_mensagem(f"Erro ao acessar o banco: {erro.msg}")

    def limpar_formulario(self):
        self.txt_titulo.set_text("")
        self.txt_genero.set_text("")
        self.txt_plataforma.set_text("")
        self.txt_capitulo.set_text("")
        self.txt_data.set_text("")
        self.txt_avaliacao.set_text("")
        self.id_em_edicao = None
        self.btn_gravar.set_label("Gravar")

    def ao_gravar(self, componente=None, dados=None):
        """CREATE ou UPDATE"""
        titulo = self.txt_titulo.get_text().strip()
        genero = self.txt_genero.get_text().strip()
        plataforma = self.txt_plataforma.get_text().strip()
        qtd_capitulos = self.txt_capitulo.get_text().strip()
        data = self.txt_data.get_text().strip()
        avaliacao = self.txt_avaliacao.get_text().strip()
        if not titulo:
            self.mostrar_mensagem("Informe o nome do dorama.")
            return
        try:
            if self.id_em_edicao is None:
                repo.inserir(titulo, genero, plataforma, qtd_capitulos, data, avaliacao)
                self.mostrar_mensagem(f"Dorama \"{titulo}\" gravado.")
            else:
                repo.atualizar(self.id_em_edicao, titulo, genero, plataforma, qtd_capitulos, data, avaliacao)
                self.mostrar_mensagem(f"Dorama \"{titulo}\" alterado.")
        except mysql.connector.Error as erro:
            if erro.errno == 1062:          
                self.mostrar_mensagem(f"Já existe um dorama chamado \"{titulo}\".")
            else:
                self.mostrar_mensagem(f"Erro ao gravar: {erro.msg}")
            return
        self.limpar_formulario()
        self.carregar_tabela()

    def linha_selecionada(self):
        modelo, posicao = self.selecao.get_selected()
        if posicao is None:
            return None
        return modelo[posicao][0], modelo[posicao][1], modelo[posicao][2]

    def ao_mudar_selecao(self, componente=None, dados=None):
        tem_selecao = self.linha_selecionada() is not None
        self.btn_editar.set_sensitive(tem_selecao)
        self.btn_excluir.set_sensitive(tem_selecao)

    def ao_editar(self, componente=None, dados=None):
        linha = self.linha_selecionada()
        if linha is None:
            return
        self.id_dorama, titulo, genero, plataforma, qtd_capitulos, data, avaliacao = linha
        self.txt_titulo.set_text(titulo)
        self.txt_genero.set_text(genero)
        self.txt_plataforma.set_text(plataforma)
        self.txt_capitulo.set_text(qtd_capitulos)
        self.txt_data.set_text(data)
        self.txt_avaliacao.set_text(avaliacao)
        self.id_em_edicao = self.id_dorama
        self.btn_gravar.set_label("Salvar Alteração")
        self.mostrar_mensagem(f"Editando dorama \"{titulo}\".")

    def ao_excluir(self, componente=None, dados=None):
        linha = self.linha_selecionada()
        if linha is None:
            return
        id_dorama, titulo, _ = linha
        dialogo = Gtk.MessageDialog(
            transient_for=self.janela,     
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Excluir o dorama \"{titulo}\"?",
        )
        resposta = dialogo.run()
        dialogo.destroy()
        if resposta != Gtk.ResponseType.YES:
            return
        try:
            repo.excluir(id_dorama)
            self.mostrar_mensagem(f"Dorama \"{titulo}\" excluído.")
        except mysql.connector.Error as erro:
            if erro.errno == 1451:        
                self.mostrar_mensagem(f"\"{titulo}\" não pode ser excluído: existem lançamentos neste dorama.")
            else:
                self.mostrar_mensagem(f"Erro ao excluir: {erro.msg}")
            return
        self.limpar_formulario()
        self.carregar_tabela()

if __name__ == "__main__":
    Aplicacao()
    Gtk.main()