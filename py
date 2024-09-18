import sys
import traceback
import flet as ft
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Produto(Base):
    __tablename__ = 'produtos'
    id = Column(Integer, primary_key=True)
    numero_op = Column(String)
    numero_nf = Column(String)
    endereco = Column(String)

engine = create_engine('sqlite:///dados.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def main(page: ft.Page):
    try:
        page.title = "App de Endereçamento"

        def cadastro(e):
            numero_op = produto.value
            numero_nf = NF.value
            endereco = enderecamento.value

            produto_existente = session.query(Produto).filter_by(endereco=endereco).first()
            if produto_existente:
                aviso.value = f"Já existe um produto cadastrado neste endereço: {produto_existente.numero_op}"
            else:
                novo_produto = Produto(numero_op=numero_op, numero_nf=numero_nf, endereco=endereco)
                session.add(novo_produto)
                session.commit()
                produto.value = ''
                NF.value = ''
                enderecamento.value = ''
                aviso.value = "Produto cadastrado com sucesso!"

            atualizar_tabela()
            page.update()

        def atualizar_tabela(filtro=None):
            produtos = session.query(Produto)
            if filtro:
                produtos = produtos.filter(
                    (Produto.numero_op.contains(filtro)) |
                    (Produto.endereco.contains(filtro))
                )
            produtos = produtos.all()
            table.rows.clear()
            for prod in produtos:
                table.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(prod.id))),
                    ft.DataCell(ft.Text(prod.numero_op)),
                    ft.DataCell(ft.Text(prod.numero_nf)),
                    ft.DataCell(ft.Text(prod.endereco)),
                    ft.DataCell(ft.IconButton(ft.icons.EDIT, on_click=lambda e, p=prod: editar_produto(p))),
                    ft.DataCell(ft.IconButton(ft.icons.DELETE, on_click=lambda e, p=prod: excluir_produto(p)))
                ]))
            page.update()

        def pesquisar(e):
            filtro = pesquisa.value.strip()
            atualizar_tabela(filtro)

        def editar_produto(produto):
            produto_id.value = str(produto.id)
            produto_numero_op.value = produto.numero_op
            produto_numero_nf.value = produto.numero_nf
            produto_endereco.value = produto.endereco
            dlg_editar.open = True
            page.update()

        def salvar_edicao(e):
            prod_id = int(produto_id.value)
            prod = session.query(Produto).filter_by(id=prod_id).first()
            prod.numero_op = produto_numero_op.value
            prod.numero_nf = produto_numero_nf.value
            prod.endereco = produto_endereco.value
            session.commit()
            dlg_editar.open = False
            atualizar_tabela()
            page.update()

        def excluir_produto(produto):
            session.delete(produto)
            session.commit()
            atualizar_tabela()

        txt_titulo = ft.Text('Numero da OP:')
        produto = ft.TextField(label="Digite o Numero da Ordem de Produção...", text_align=ft.TextAlign.LEFT)
        txt_NF = ft.Text("Numero da NF")
        NF = ft.TextField(label="Digite o numero da Nota Fiscal...", text_align=ft.TextAlign.LEFT)
        txt_enderecamento = ft.Text('Endereçamento:')
        enderecamento = ft.TextField(label="Digite a Rua/Modulo/Posição...", text_align=ft.TextAlign.LEFT)
        bnt_produto = ft.ElevatedButton('Cadastrar', on_click=cadastro)
        aviso = ft.Text('', color=ft.colors.RED)  # Aviso para produtos duplicados ou sucesso

        pesquisa = ft.TextField(label="Pesquisar por OP ou Endereço...")

        btn_pesquisar = ft.ElevatedButton('Pesquisar', on_click=pesquisar)

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Numero OP")),
                ft.DataColumn(ft.Text("Numero NF")),
                ft.DataColumn(ft.Text("Endereço")),
                ft.DataColumn(ft.Text("Editar")),
                ft.DataColumn(ft.Text("Excluir")),
            ],
            rows=[]
        )

        produto_id = ft.TextField(visible=False)
        produto_numero_op = ft.TextField(label="Numero da OP")
        produto_numero_nf = ft.TextField(label="Numero da NF")
        produto_endereco = ft.TextField(label="Endereço")
        dlg_editar = ft.AlertDialog(
            title=ft.Text("Editar Produto"),
            content=ft.Column([
                produto_id,
                produto_numero_op,
                produto_numero_nf,
                produto_endereco
            ]),
            actions=[
                ft.ElevatedButton("Salvar", on_click=salvar_edicao),
                ft.ElevatedButton("Cancelar", on_click=lambda e: dlg_editar.set_open(False)),
            ],
        )

        page.add(
            txt_titulo,
            produto,
            txt_NF,
            NF,
            txt_enderecamento,
            enderecamento,
            bnt_produto,
            aviso,
            pesquisa,
            btn_pesquisar,  # Adiciona o botão de pesquisa
            table,  # Adicionando a tabela diretamente à página
            dlg_editar
        )

        # Configura rolagem para a página
        page.scroll = ft.ScrollMode.AUTO
        page.update()

        atualizar_tabela()  # Inicializa a tabela com todos os produtos

    except Exception as e:
        print("Ocorreu um erro:", e)
        traceback.print_exc()

ft.app(target=main)
