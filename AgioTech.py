import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import os

COR_PRIMARIA = "#ff6500"
COR_SECUNDARIA = "#ff914d"
COR_DESTAQUE = "#cc3300"
COR_FUNDO = "#fff7eb"

# BANCO DE DADOS

if not os.path.exists("AgioTech.db"):
    open("AgioTech.db", "w").close() 

conn = sqlite3.connect("AgioTech.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT,
    data_nascimento TEXT,
    cpf TEXT,
    renda_mensal REAL,
    gastos_mensais REAL,
    elegivel INTEGER,
    limite_emprestimo REAL,
    valor_solicitado REAL,
    prazo_meses INTEGER,
    taxa_juros REAL,
    parcela_mensal REAL,
    total_a_pagar REAL,
    criado_em TEXT
)
""")
conn.commit()


# ERROS
def to_float(value, field_name):
    if value is None:
        raise ValueError(f"{field_name} inválido (vazio).")
    s = str(value).strip()
    if s == "":
        raise ValueError(f"{field_name} inválido (vazio).")
    try:
        return float(s)
    except Exception:
        raise ValueError(f"{field_name} inválido (deve ser número).")


def to_int(value, field_name):
    if value is None:
        raise ValueError(f"{field_name} inválido (vazio).")
    s = str(value).strip()
    if s == "":
        raise ValueError(f"{field_name} inválido (vazio).")
    try:
        return int(s)
    except Exception:
        raise ValueError(f"{field_name} inválido (deve ser inteiro).")


# FUNÇÕES CÁLCULO
def calcular_idade(data_nasc):
    nasc = datetime.strptime(data_nasc, "%d/%m/%Y").date()
    hoje = date.today()
    return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))


def calcular_limite(renda):
    return renda * 1.5 if renda <= 3000 else renda * 2.5


def calcular_juros(prazo):
    if prazo <= 6:
        return 0
    elif prazo <= 12:
        return 0.02
    elif prazo <= 18:
        return 0.04
    else:
        return 0.06


# TROCA DE TELA
def mostrar_tela(tela):
    for widget in root.winfo_children():
        widget.destroy()
    tela()


# TELA INICIAL
def tela_inicial():
    tk.Label(root, text="AgioTech", font=("Arial Black", 40), fg=COR_PRIMARIA, bg=COR_FUNDO).pack(pady=60)
    tk.Button(root, text="Cadastro / Simulação", bg=COR_PRIMARIA, fg="white", font=("Arial", 16),
              width=25, height=2, command=lambda: mostrar_tela(tela_cadastro)).pack(pady=10)
    tk.Button(root, text="Banco de Dados", bg=COR_PRIMARIA, fg="white", font=("Arial", 16),
              width=25, height=2, command=lambda: mostrar_tela(tela_banco)).pack(pady=10)


# TELA CADASTRO / SIMULAÇÃO
def tela_cadastro():
    for widget in root.winfo_children():
        widget.destroy()

    def simular():
        try:
            renda = to_float(entry_renda.get(), "Renda")
            gastos = to_float(entry_gastos.get(), "Gastos")
            valor = to_float(entry_valor.get(), "Valor desejado")
            prazo = to_int(entry_prazo.get(), "Prazo (meses)")
            idade = calcular_idade(entry_data.get())

            if idade < 18:
                messagebox.showerror("Erro", "Cliente deve ter pelo menos 18 anos.")
                return
            if renda < 1000:
                messagebox.showerror("Erro", "Renda mínima de R$ 1.000.")
                return
            if gastos > 0.7 * renda:
                messagebox.showwarning("Aviso", "Gastos mensais superiores a 70% da renda. Cliente inelegível.")
                return

            limite = calcular_limite(renda)
            if valor > limite:
                messagebox.showwarning("Aviso", f"Valor solicitado excede o limite máximo de R$ {limite:.2f}")
                return

            taxa = calcular_juros(prazo)
            total = valor * (1 + taxa)
            parcela = total / prazo if prazo > 0 else 0

            resultado = (
                f"Limite de Empréstimo: R$ {limite:.2f}\n"
                f"Taxa de Juros: {(taxa * 100):.1f}%\n"
                f"Total a Pagar: R$ {total:.2f}\n"
                f"Valor da Parcela: R$ {parcela:.2f}"
            )
            messagebox.showinfo("Simulação", resultado)
        except Exception as e:
            messagebox.showerror("Erro na Simulação", f"Preencha os campos corretamente.\nDetalhe: {e}")

    def salvar():
        try:
            nome = entry_nome.get().strip()
            telefone = entry_tel.get().strip()
            data_nasc = entry_data.get().strip()
            cpf = entry_cpf.get().strip()
            renda = to_float(entry_renda.get(), "Renda")
            gastos = to_float(entry_gastos.get(), "Gastos")
            valor_solicitado = to_float(entry_valor.get(), "Valor solicitado")
            prazo = to_int(entry_prazo.get(), "Prazo (meses)")

            if not all([nome, telefone, data_nasc, cpf]):
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            if len(cpf) != 11 or not cpf.isdigit():
                messagebox.showerror("Erro", "CPF deve ter 11 dígitos numéricos.")
                return

            idade = calcular_idade(data_nasc)
            if idade < 18 or renda < 1000 or gastos > 0.7 * renda:
                elegivel = 0
                limite = 0
            else:
                elegivel = 1
                limite = calcular_limite(renda)

            taxa = calcular_juros(prazo)
            total = valor_solicitado * (1 + taxa)
            parcela = total / prazo if prazo > 0 else 0
            criado_em = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            cursor.execute("""
                INSERT INTO clientes (nome, telefone, data_nascimento, cpf, renda_mensal, gastos_mensais, elegivel,
                limite_emprestimo, valor_solicitado, prazo_meses, taxa_juros, parcela_mensal,
                total_a_pagar, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, telefone, data_nasc, cpf, renda, gastos, elegivel, limite, valor_solicitado,
                  prazo, taxa, parcela, total, criado_em))
            conn.commit()

            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Verifique os dados inseridos.\nDetalhe: {e}")

    tk.Label(root, text="Cadastro / Simulação de Empréstimo", font=("Arial Black", 20),
             bg=COR_FUNDO, fg=COR_PRIMARIA).pack(pady=20)

    frame = tk.Frame(root, bg=COR_FUNDO)
    frame.pack(pady=10)

    labels = ["Nome", "Telefone", "Data de Nascimento (dd/mm/aaaa)", "CPF", "Renda Mensal (R$)",
              "Gastos Mensais (R$)", "Valor Desejado (R$)", "Prazo (meses)"]
    entradas = []
    for i, texto in enumerate(labels):
        tk.Label(frame, text=texto, bg=COR_FUNDO, fg="black", font=("Arial", 12)).grid(row=i, column=0, sticky="w", pady=5)
        e = tk.Entry(frame, width=40)
        e.grid(row=i, column=1, pady=5, padx=10)
        entradas.append(e)

    entry_nome, entry_tel, entry_data, entry_cpf, entry_renda, entry_gastos, entry_valor, entry_prazo = entradas

    frame_botoes = tk.Frame(root, bg=COR_FUNDO)
    frame_botoes.pack(pady=15)

    tk.Button(frame_botoes, text="Simular Empréstimo", bg=COR_PRIMARIA, fg="white", font=("Arial", 12),
              width=18, command=simular).grid(row=0, column=0, padx=10)
    tk.Button(frame_botoes, text="Salvar Cadastro", bg=COR_PRIMARIA, fg="white", font=("Arial", 12),
              width=18, command=salvar).grid(row=0, column=1, padx=10)
    tk.Button(frame_botoes, text="Voltar", bg=COR_SECUNDARIA, fg="white", font=("Arial", 12),
              width=18, command=lambda: mostrar_tela(tela_inicial)).grid(row=0, column=2, padx=10)


# TELA BANCO DE DADOS
def tela_banco():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Banco de Dados - Clientes", font=("Arial Black", 20),
             bg=COR_FUNDO, fg=COR_PRIMARIA).pack(pady=10)

    frame = tk.Frame(root, bg=COR_FUNDO)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    colunas = ("ID", "Nome", "Telefone", "Nascimento", "CPF", "Renda", "Gastos", "Elegível",
               "Limite", "Valor Solicitado", "Prazo", "Taxa", "Parcela", "Total", "Criado em")

    tree = ttk.Treeview(frame, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    tree.tag_configure('oddrow', background="#fff7eb")
    tree.tag_configure('evenrow', background="#ffefd5")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    tree.pack(fill="both", expand=True)

    def atualizar_tabela():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute("SELECT * FROM clientes ORDER BY criado_em DESC LIMIT 100")
        registros = cursor.fetchall()
        for i, linha in enumerate(registros):
            (
                id_, nome, telefone, data_nascimento, cpf, renda_mensal, gastos_mensais, elegivel,
                limite_emprestimo, valor_solicitado, prazo_meses, taxa, parcela_mensal,
                total_a_pagar, criado_em
            ) = linha
            taxa_text = f"{(float(taxa) * 100):.1f}%" if taxa is not None else "-"
            elegivel_text = "Sim" if elegivel == 1 else "Não"
            tree.insert("", "end", values=(
                id_, nome, telefone, data_nascimento, cpf,
                f"R$ {renda_mensal:.2f}", f"R$ {gastos_mensais:.2f}", elegivel_text,
                f"R$ {limite_emprestimo:.2f}" if limite_emprestimo else "-",
                f"R$ {valor_solicitado:.2f}" if valor_solicitado else "-",
                prazo_meses if prazo_meses else "-",
                taxa_text,
                f"R$ {parcela_mensal:.2f}" if parcela_mensal else "-",
                f"R$ {total_a_pagar:.2f}" if total_a_pagar else "-",
                criado_em
            ), tags=('evenrow' if i % 2 == 0 else 'oddrow',))

    def deletar():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return
        id_cliente = tree.item(selecionado[0])['values'][0]
        cursor.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
        conn.commit()
        atualizar_tabela()
        messagebox.showinfo("Sucesso", "Cliente removido!")

    def editar():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
        id_cliente = tree.item(selecionado[0])['values'][0]
        cursor.execute("SELECT * FROM clientes WHERE id=?", (id_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado.")
            return

        edit_win = tk.Toplevel(root)
        edit_win.title("Editar Cliente")
        edit_win.config(bg=COR_FUNDO)
        edit_win.geometry("480x600")

        frame_central = tk.Frame(edit_win, bg=COR_FUNDO)
        frame_central.place(relx=0.5, rely=0.5, anchor="center")

        labels = [
            "Nome", "Telefone", "Data de Nascimento", "CPF",
            "Renda Mensal", "Gastos Mensais", "Valor Solicitado", "Prazo (meses)"
        ]
        campos = []
        for i, campo in enumerate(labels):
            tk.Label(frame_central, text=campo, bg=COR_FUNDO, fg="black",
                    font=("Arial", 12)).grid(row=i, column=0, pady=8, sticky="e", padx=10)
            entry = tk.Entry(frame_central, width=35)
            entry.grid(row=i, column=1, pady=8, padx=10)
            campos.append(entry)

        entry_nome, entry_tel, entry_data, entry_cpf, entry_renda, entry_gastos, entry_valor, entry_prazo = campos

        entry_nome.insert(0, cliente[1])
        entry_tel.insert(0, cliente[2])
        entry_data.insert(0, cliente[3])
        entry_cpf.insert(0, cliente[4])
        entry_renda.insert(0, cliente[5] if cliente[5] is not None else "")
        entry_gastos.insert(0, cliente[6] if cliente[6] is not None else "")
        entry_valor.insert(0, cliente[9] if cliente[9] is not None else cliente[8] if cliente[8] is not None else "")
        entry_prazo.insert(0, cliente[10] if cliente[10] is not None else "")

        def salvar_edicao():
            try:
                novo_nome = entry_nome.get().strip()
                novo_tel = entry_tel.get().strip()
                nova_data = entry_data.get().strip()
                novo_cpf = entry_cpf.get().strip()
                nova_renda = to_float(entry_renda.get(), "Renda")
                novo_gastos = to_float(entry_gastos.get(), "Gastos")
                novo_valor = to_float(entry_valor.get(), "Valor solicitado")
                novo_prazo = to_int(entry_prazo.get(), "Prazo (meses)")

                idade = calcular_idade(nova_data)
                if idade < 18 or nova_renda < 1000 or novo_gastos > 0.7 * nova_renda:
                    elegivel = 0
                    limite = 0
                else:
                    elegivel = 1
                    limite = calcular_limite(nova_renda)

                taxa = calcular_juros(novo_prazo)
                total = novo_valor * (1 + taxa)
                parcela = total / novo_prazo if novo_prazo > 0 else 0

                cursor.execute("""
                    UPDATE clientes
                    SET nome=?, telefone=?, data_nascimento=?, cpf=?, renda_mensal=?, gastos_mensais=?, elegivel=?, 
                        limite_emprestimo=?, valor_solicitado=?, prazo_meses=?, taxa_juros=?, parcela_mensal=?, total_a_pagar=?
                    WHERE id=?
                """, (novo_nome, novo_tel, nova_data, novo_cpf, nova_renda, novo_gastos, elegivel,
                      limite, novo_valor, novo_prazo, taxa, parcela, total, id_cliente))
                conn.commit()
                atualizar_tabela()
                messagebox.showinfo("Sucesso", "Cliente atualizado!")
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Erro ao Atualizar", f"Verifique os dados inseridos.\nDetalhe: {e}")

        tk.Button(frame_central, text="Salvar Alterações", bg=COR_PRIMARIA, fg="white",
                  font=("Arial", 12), command=salvar_edicao).grid(row=len(labels), columnspan=2, pady=20)

    frame_botoes = tk.Frame(root, bg=COR_FUNDO)
    frame_botoes.pack(pady=15)

    tk.Button(frame_botoes, text="Atualizar", bg=COR_DESTAQUE, fg="white", font=("Arial", 12),
              width=15, command=atualizar_tabela).grid(row=0, column=0, padx=10)
    tk.Button(frame_botoes, text="Editar Dados", bg=COR_DESTAQUE, fg="white", font=("Arial", 12),
              width=15, command=editar).grid(row=0, column=1, padx=10)
    tk.Button(frame_botoes, text="Excluir Selecionado", bg=COR_DESTAQUE, fg="white", font=("Arial", 12),
              width=20, command=deletar).grid(row=0, column=2, padx=10)
    tk.Button(frame_botoes, text="Voltar", bg=COR_SECUNDARIA, fg="white", font=("Arial", 12),
              width=15, command=lambda: mostrar_tela(tela_inicial)).grid(row=0, column=3, padx=10)

    atualizar_tabela()


# RODAR
root = tk.Tk()
root.title("AgioTech - Sistema de Empréstimos Pessoais")
root.geometry("1100x650")
root.config(bg=COR_FUNDO)
tela_inicial()
root.mainloop()
