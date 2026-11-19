# -*- coding: utf-8 -*-

import repositorio_doramas as repo
print("Antes:", repo.listar())
repo.inserir("Amor Rural", "Comédia Romantica", "Netflix", 12)
print("Depois de inserir:", repo.listar())
id_amorRual = [c[0] for c in repo.listar() if c[1] == "Farmacia"][0]
repo.atualizar(id_amorRual, "Amor e Batatas", "Comédia Romantica", "Netflix", 12)
print("Depois de atualizar:", repo.listar())
repo.excluir(id_amorRual)
print("Depois de excluir:", repo.listar())