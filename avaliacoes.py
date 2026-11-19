#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import mysql.connector
import repositorio_doramas
import repositorio_avaliacoes as repo
import repositorio_usuario

def texto_para_data(texto):
    """Converte 'dd/mm/aaaa' em date. Lança ValueError se o texto for inválido."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").date()

def data_para_texto(data):
    """Converte um date em texto no formato 'dd/mm/aaaa'."""
    return data.strftime("%d/%m/%Y")

class Aplicacao:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file("avaliacoes.glade")
     
        self.janela = builder.get_object("janela")
        self.mni_lancamentos = builder.get_object("mni_lancamentos")
        self.mni_lancamentos.connect("activate", self.ao_menu_lancamentos)
        self.mni_usuarios = builder.get_object("mni_usuarios")
        self.mni_usuarios.connect("activate", self.ao_menu_usuarios)
        self.mni_sair = builder.get_object("mni_sair")
        self.mni_sair.connect("activate", self.ao_menu_sair)
        self.mni_sobre = builder.get_object("mni_sobre")
        self.mni_sobre.connect("activate", self.ao_menu_sobre)
 
        self.ent_data_inicial = builder.get_object("ent_data_inicial")

        self.btn_buscar = builder.get_object("btn_buscar")
        self.btn_buscar.connect("clicked", self.ao_buscar)
        self.btn_todos = builder.get_object("btn_todos")
        self.btn_todos.connect("clicked", self.ao_mostrar_todos)
        self.btn_gerar_pdf = builder.get_object("btn_gerar_pdf")
        self.btn_gerar_pdf.connect("clicked", self.ao_gerar_pdf)
        
        self.tvw_avaliacoes = builder.get_object("tvw_avaliacoes")
        self.lst_avaliacoes = builder.get_object("lst_avaliacoes")
        
        self.ent_data = builder.get_object("ent_data")
        self.ent_nota = builder.get_object("ent_nota")
        self.ent_descricao = builder.get_object("ent_descricao")
        self.cmb_dorama = builder.get_object("cmb_dorama")
        self.cmb_usuario = builder.get_object("cmb_usuario")
        
        self.btn_gravar = builder.get_object("btn_gravar")
        self.btn_gravar.connect("clicked", self.ao_gravar)
        self.btn_editar = builder.get_object("btn_editar")
        self.btn_editar.connect("clicked", self.ao_editar)
        self.btn_excluir = builder.get_object("btn_excluir")
        self.btn_excluir.connect("clicked", self.ao_excluir)
        
        self.lbl_mensagem = builder.get_object("lbl_mensagem")
        self.selecao = self.tvw_avaliacoes.get_selection()
        self.selecao.connect("changed", self.ao_mudar_selecao)
        self.id_em_edicao = None

        # None = mostrar todos; (data_inicial, data_final) = pesquisa ativa
        self.periodo = None
        self.janela.connect("destroy", Gtk.main_quit)
        
        self.carregar_listas()
        self.limpar_formulario()
        self.carregar_tabela()
        self.janela.show_all()

    def mostrar_mensagem(self, texto):
        self.lbl_mensagem.set_text(texto)
     
    def carregar_tabela(self):
        """Carrega as avaliações do banco de dados na tabela."""
        self.lst_avaliacoes.clear()
        try:
            avaliacoes = repo.listar()
            for id_avaliacao, data, nota, descricao, dorama_id, usuario_id in avaliacoes:
                valores = [
                    int(id_avaliacao),
                    data_para_texto(data),
                    float(nota),
                    str(descricao),
                    int(dorama_id),
                    int(usuario_id)
                ]
                # Diagnóstico temporário: mostra os tipos das colunas
                print("\n--- TIPOS DAS COLUNAS ---", flush=True)
                for i in range(self.lst_avaliacoes.get_n_columns()):
                    tipo = self.lst_avaliacoes.get_column_type(i)
                    print(f"Coluna {i}: {tipo.name}", flush=True)
                # Mostra os valores e seus tipos
                print("\n--- VALORES ENVIADOS ---", flush=True)
                for i, valor in enumerate(valores):
                    print(
                        f"Valor {i}: {valor!r} "
                        f"({type(valor).__name__})",
                        flush=True
                    )
                self.lst_avaliacoes.append(valores)
        except mysql.connector.Error as erro:
            self.mostrar_mensagem(
                f"Erro ao acessar o banco: {erro.msg}"
            )

    def carregar_listas(self):
        """Preenche as listas de categorias e de membros com os dados do banco."""
        self.cmb_dorama.remove_all()
        self.cmb_usuario.remove_all()
        try:
            for id_dorama, titulo, genero, plataforma, qtd_capitulos in repositorio_doramas.listar():
                self.cmb_dorama.append(str(id_dorama), str(titulo))
            for id_usuario, nome, login in repositorio_usuario.listar():
                self.cmb_usuario.append(str(id_usuario), str(nome))
        except mysql.connector.Error as erro:
            self.mostrar_mensagem(f"Erro ao acessar o banco: {erro.msg}")

    def limpar_formulario(self):
        self.ent_data.set_text(data_para_texto(date.today()))
        self.ent_nota.set_text("")
        self.ent_descricao.set_text("")
        self.cmb_dorama.set_active(-1)  
        self.cmb_usuario.set_active(-1)
        self.id_em_edicao = None
        self.btn_gravar.set_label("Gravar")

    def ao_buscar(self, componente=None, dados=None):
        """Filtra a tabela pelo período informado."""
        try:
            data_inicial = texto_para_data(self.ent_data_inicial.get_text())
        except ValueError:
            self.mostrar_mensagem("Informe as duas datas no formato dd/mm/aaaa.")
            return
        self.periodo = (data_inicial)
        self.carregar_tabela()
        self.mostrar_mensagem(f"{len(self.lst_avaliacoes)} Avaliação(ões) do dia "
                              f"{data_para_texto(data_inicial)}.")

    def ao_mostrar_todos(self, componente=None, dados=None):
        """Desfaz a pesquisa e volta a mostrar todos os lançamentos."""
        self.periodo = None
        self.ent_data_inicial.set_text("")
        self.carregar_tabela()
        self.mostrar_mensagem(f"Mostrando todos os {len(self.lst_avaliacoes)} avaliações.")

    def ao_gravar(self, componente=None, dados=None):
        """CREATE ou UPDATE: grava um lançamento novo ou o que está em edição."""
        descricao = self.ent_descricao.get_text().strip()
        dorama_id = self.cmb_dorama.get_active_id()     
        usuario_id = self.cmb_usuario.get_active_id()
        try:
            data = texto_para_data(self.ent_data.get_text())
        except ValueError:
            self.mostrar_mensagem("Data inválida. Use o formato dd/mm/aaaa.")
            return
        try:
            nota = Decimal(self.ent_nota.get_text().strip().replace(",", "."))
        except InvalidOperation:
            self.mostrar_mensagem("Valor inválido. Use vírgula para os centavos, como em 45,90.")
            return
        if nota <= 0:
            self.mostrar_mensagem("A nota deve ser maior que zero.")
            return
        if not descricao or dorama_id is None or usuario_id is None:
            self.mostrar_mensagem("Preencha a descrição e escolha o dorama e o usuário.")
            return
        try:
            if self.id_em_edicao is None:
                repo.inserir(data, descricao, nota, int(usuario_id), int(dorama_id))
                self.mostrar_mensagem(f"Avaliação \"{descricao}\" gravado.")
            else:
                repo.atualizar(self.id_em_edicao, data, descricao, nota, int(usuario_id), int(dorama_id))
                self.mostrar_mensagem(f"Lançamento \"{descricao}\" alterado.")
        except mysql.connector.Error as erro:
            self.mostrar_mensagem(f"Erro ao gravar: {erro.msg}")
            return
        self.limpar_formulario()
        self.carregar_tabela()

    def linha_selecionada(self):
        modelo, posicao = self.selecao.get_selected()
        if posicao is None:
            return None
        return modelo[posicao][0], modelo[posicao][1], modelo[posicao][2]

    def ao_excluir(self, componente=None, dados=None):
        """DELETE: pede confirmação e apaga o lançamento selecionado."""
        linha = self.linha_selecionada()
        if linha is None:
            return
        id_avaliacao, data_texto, descricao = linha
        dialogo = Gtk.MessageDialog(
            transient_for=self.janela,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Excluir a avaliação \"{descricao}\" de {data_texto}?",
        )
        resposta = dialogo.run()
        dialogo.destroy()
        if resposta != Gtk.ResponseType.YES:
            return
        try:
            repo.excluir(id_avaliacao)
            self.mostrar_mensagem(f"Avaliação \"{descricao}\" excluída.")
        except mysql.connector.Error as erro:
            self.mostrar_mensagem(f"Erro ao excluir: {erro.msg}")
            return
        self.limpar_formulario()
        self.carregar_tabela()

    def ao_menu_lancamentos(self, componente=None, dados=None):
        self.carregar_listas()
        self.limpar_formulario()
        self.ao_mostrar_todos()

    def ao_menu_usuarios(self, componente=None, dados=None):
        """Abre o cadastro de usuários em uma janela separada."""
        subprocess.Popen([sys.executable, "usuarios.py"])

    def ao_menu_sair(self, componente=None, dados=None):
       self.janela.destroy()

    def ao_menu_sobre(self, componente=None, dados=None):
        """Mostra a janela 'Sobre' com as informações do sistema."""
        dialogo = Gtk.AboutDialog(
            transient_for=self.janela,
            modal=True,
            program_name="Avaliação de Doramas",
            version="1.0",
            comments="Sistema de avaliação de doramas.\n"
                     "Projeto da disciplina Linguagem de Programação II da UFCI",
            authors=["Manu, Gustavo, Letícia"],
        )
        dialogo.run()
        dialogo.destroy()

    def ao_gerar_pdf(self, componente=None, dados=None):
        self.mostrar_mensagem("Em breve: o relatório em PDF será construído na próxima aula.")

    def ao_editar(self, componente=None, dados=None):
            linha = self.linha_selecionada()
            if linha is None:
                return
            self.id_avaliacao, data, descricao, nota, usuario_id, dorama_id = linha
            self.ent_data.set_text(data)
            self.ent_descricao.set_text(descricao)
            self.ent_nota.set_text(nota)
            self.ent_usuario_id.set_text(str(usuario_id))
            self.ent_dorama_id.set_text(str(dorama_id))
            self.id_em_edicao = self.id_avaliacao
            self.btn_gravar.set_label("Salvar Alteração")
            self.mostrar_mensagem(f"Editando a avaliação do dorama\"{dorama_id}\".")

    def ao_mudar_selecao(self, componente=None, dados=None):
            tem_selecao = self.linha_selecionada() is not None
            self.btn_editar.set_sensitive(tem_selecao)
            self.btn_excluir.set_sensitive(tem_selecao)
    

if __name__ == "__main__":
    Aplicacao()
    Gtk.main()