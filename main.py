
from datetime import datetime
import math
import tkinter as tk
from tkinter import ttk, messagebox


# ==========================================
# CLASSE VEICULO
# ==========================================

class Veiculo:

    TARIFA_HORA = {
        "Carro": 5.0,
        "Moto": 3.0
    }

    def __init__(self, placa, modelo, tipo):
        self.placa = placa.strip().upper()
        self.modelo = modelo.strip()
        self.tipo = tipo.strip().capitalize()

        if self.tipo not in self.TARIFA_HORA:
            raise ValueError("Tipo de veículo inválido!")

    def tarifa_hora(self):
        return self.TARIFA_HORA[self.tipo]


# ==========================================
# CLASSE VAGA
# ==========================================

class Vaga:

    def __init__(self, numero, veiculo=None):
        self.numero = numero
        self.veiculo = veiculo

    @property
    def livre(self):
        return self.veiculo is None

    @property
    def ocupada(self):
        return self.veiculo is not None

    def ocupar(self, veiculo):
        self.veiculo = veiculo

    def liberar(self):
        self.veiculo = None


# ==========================================
# CLASSE TICKET
# ==========================================

class Ticket:

    TOLERANCIA_MINUTOS = 15
    DIARIA_MAX = 24 * 60

    def __init__(self, veiculo, vaga):
        self.veiculo = veiculo
        self.vaga = vaga
        self.entrada = datetime.now()
        self.saida = None
        self.valor = 0.0
        self.forma_pagamento = None

    def minutos_estacionado(self, ate=None):
        ate = ate or datetime.now()
        return (ate - self.entrada).total_seconds() / 60

    def calcular_valor(self, ate=None):

        minutos = self.minutos_estacionado(ate)

        if minutos <= self.TOLERANCIA_MINUTOS:
            return 0.0

        horas = math.ceil(minutos / 60)
        horas = min(horas, self.DIARIA_MAX / 60)

        return horas * self.veiculo.tarifa_hora()


# ==========================================
# CLASSE ESTACIONAMENTO
# ==========================================

class Estacionamento:

    def __init__(self, total_vagas=10):

        self.vagas = [
            Vaga(numero=i + 1)
            for i in range(total_vagas)
        ]

        self.tickets_abertos = {}
        self.historico = []
        self.arrecadado = 0.0

    def primeira_vaga_livre(self):

        for vaga in self.vagas:
            if vaga.livre:
                return vaga

        return None

    def registrar_entrada(self, veiculo):

        if veiculo.placa in self.tickets_abertos:
            raise ValueError("Este veículo já está no estacionamento.")

        vaga = self.primeira_vaga_livre()

        if vaga is None:
            raise ValueError("Estacionamento lotado.")

        vaga.ocupar(veiculo)

        ticket = Ticket(veiculo, vaga)

        self.tickets_abertos[veiculo.placa] = ticket

        return ticket

    def buscar_ticket(self, placa):

        return self.tickets_abertos.get(
            placa.strip().upper()
        )

    def registrar_saida(self, placa, forma_pagamento):

        ticket = self.buscar_ticket(placa)

        if ticket is None:
            raise ValueError("Veículo não encontrado no estacionamento.")

        ticket.saida = datetime.now()
        ticket.valor = ticket.calcular_valor()
        ticket.forma_pagamento = forma_pagamento

        ticket.vaga.liberar()

        del self.tickets_abertos[placa.strip().upper()]

        self.historico.append(ticket)

        self.arrecadado += ticket.valor

        return ticket


# ==========================================
# CLASSE INTERFACE TKINTER
# ==========================================

class InterfaceEstacionamento:

    def __init__(self, janela):

        self.estacionamento = Estacionamento(10)

        self.janela = janela
        self.janela.title("Sistema de Estacionamento")
        self.janela.geometry("850x650")
        self.janela.resizable(False, False)

        self.criar_interface()
        self.atualizar_tabelas()

    # ======================================
    # CRIAR INTERFACE
    # ======================================

    def criar_interface(self):

        tk.Label(
            self.janela,
            text="SISTEMA DE ESTACIONAMENTO",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        # INFORMAÇÕES
        frame_info = tk.Frame(self.janela)
        frame_info.pack(pady=5)

        self.label_vagas = tk.Label(
            frame_info,
            text="Vagas disponíveis: 10",
            font=("Arial", 11, "bold")
        )
        self.label_vagas.grid(row=0, column=0, padx=20)

        self.label_arrecadado = tk.Label(
            frame_info,
            text="Total arrecadado: R$ 0.00",
            font=("Arial", 11, "bold")
        )
        self.label_arrecadado.grid(row=0, column=1, padx=20)

        # CADASTRO
        frame_cadastro = tk.LabelFrame(
            self.janela,
            text="Dados do veículo",
            padx=10,
            pady=10
        )
        frame_cadastro.pack(padx=20, pady=10, fill="x")

        tk.Label(frame_cadastro, text="Placa:").grid(row=0, column=0)
        self.campo_placa = tk.Entry(frame_cadastro, width=15)
        self.campo_placa.grid(row=0, column=1, padx=5)

        tk.Label(frame_cadastro, text="Modelo:").grid(row=0, column=2)
        self.campo_modelo = tk.Entry(frame_cadastro, width=15)
        self.campo_modelo.grid(row=0, column=3, padx=5)

        tk.Label(frame_cadastro, text="Tipo:").grid(row=0, column=4)

        self.campo_tipo = ttk.Combobox(
            frame_cadastro,
            values=["Carro", "Moto"],
            state="readonly",
            width=12
        )
        self.campo_tipo.grid(row=0, column=5, padx=5)
        self.campo_tipo.set("Carro")

        # PAGAMENTO
        frame_pagamento = tk.Frame(self.janela)
        frame_pagamento.pack(pady=5)

        tk.Label(
            frame_pagamento,
            text="Forma de pagamento:"
        ).grid(row=0, column=0, padx=5)

        self.pagamento = ttk.Combobox(
            frame_pagamento,
            values=["Dinheiro", "Cartão", "Pix"],
            state="readonly",
            width=15
        )
        self.pagamento.grid(row=0, column=1)
        self.pagamento.set("Pix")

        # BOTÕES
        frame_botoes = tk.Frame(self.janela)
        frame_botoes.pack(pady=10)

        tk.Button(
            frame_botoes,
            text="Registrar Entrada",
            width=18,
            command=self.registrar_entrada
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame_botoes,
            text="Registrar Saída",
            width=18,
            command=self.registrar_saida
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame_botoes,
            text="Atualizar",
            width=18,
            command=self.atualizar_tabelas
        ).grid(row=0, column=2, padx=5)

        # TABELA DE VEÍCULOS ATIVOS
        frame_tabela = tk.LabelFrame(
            self.janela,
            text="Veículos estacionados",
            padx=10,
            pady=10
        )
        frame_tabela.pack(padx=20, pady=5, fill="both", expand=True)

        colunas = ("placa", "modelo", "tipo", "vaga", "entrada")

        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            height=7
        )

        self.tabela.heading("placa", text="Placa")
        self.tabela.heading("modelo", text="Modelo")
        self.tabela.heading("tipo", text="Tipo")
        self.tabela.heading("vaga", text="Vaga")
        self.tabela.heading("entrada", text="Entrada")

        self.tabela.column("placa", width=120)
        self.tabela.column("modelo", width=150)
        self.tabela.column("tipo", width=100)
        self.tabela.column("vaga", width=80)
        self.tabela.column("entrada", width=150)

        self.tabela.pack(fill="both", expand=True)

        # HISTÓRICO
        frame_historico = tk.LabelFrame(
            self.janela,
            text="Histórico de saídas",
            padx=10,
            pady=10
        )
        frame_historico.pack(padx=20, pady=5, fill="both", expand=True)

        colunas_hist = ("placa", "saida", "valor", "pagamento")

        self.tabela_historico = ttk.Treeview(
            frame_historico,
            columns=colunas_hist,
            show="headings",
            height=5
        )

        self.tabela_historico.heading("placa", text="Placa")
        self.tabela_historico.heading("saida", text="Saída")
        self.tabela_historico.heading("valor", text="Valor")
        self.tabela_historico.heading("pagamento", text="Pagamento")

        self.tabela_historico.column("placa", width=120)
        self.tabela_historico.column("saida", width=150)
        self.tabela_historico.column("valor", width=100)
        self.tabela_historico.column("pagamento", width=120)

        self.tabela_historico.pack(fill="both", expand=True)

    # ======================================
    # REGISTRAR ENTRADA
    # ======================================

    def registrar_entrada(self):

        placa = self.campo_placa.get()
        modelo = self.campo_modelo.get()
        tipo = self.campo_tipo.get()

        if not placa.strip() or not modelo.strip():
            messagebox.showwarning(
                "Atenção",
                "Preencha a placa e o modelo!"
            )
            return

        try:

            veiculo = Veiculo(placa, modelo, tipo)

            ticket = self.estacionamento.registrar_entrada(veiculo)

            messagebox.showinfo(
                "Entrada registrada",
                f"Veículo: {veiculo.modelo}\n"
                f"Placa: {veiculo.placa}\n"
                f"Vaga: {ticket.vaga.numero}"
            )

            self.campo_placa.delete(0, tk.END)
            self.campo_modelo.delete(0, tk.END)

            self.atualizar_tabelas()

        except ValueError as erro:

            messagebox.showerror("Erro", str(erro))

    # ======================================
    # REGISTRAR SAÍDA
    # ======================================

    def registrar_saida(self):

        placa = self.campo_placa.get().strip()
        forma_pagamento = self.pagamento.get()

        if not placa:
            messagebox.showwarning(
                "Atenção",
                "Digite a placa do veículo!"
            )
            return

        try:

            ticket = self.estacionamento.registrar_saida(
                placa,
                forma_pagamento
            )

            messagebox.showinfo(
                "Saída registrada",
                f"Veículo: {ticket.veiculo.modelo}\n"
                f"Placa: {ticket.veiculo.placa}\n"
                f"Vaga: {ticket.vaga.numero}\n"
                f"Entrada: {ticket.entrada.strftime('%H:%M:%S')}\n"
                f"Saída: {ticket.saida.strftime('%H:%M:%S')}\n"
                f"Pagamento: {ticket.forma_pagamento}\n"
                f"Valor: R$ {ticket.valor:.2f}"
            )

            self.campo_placa.delete(0, tk.END)

            self.atualizar_tabelas()

        except ValueError as erro:

            messagebox.showerror("Erro", str(erro))

    # ======================================
    # ATUALIZAR TABELAS
    # ======================================

    def atualizar_tabelas(self):

        # LIMPAR TABELA DE VEÍCULOS
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        # LISTAR VEÍCULOS ESTACIONADOS
        for placa, ticket in self.estacionamento.tickets_abertos.items():

            self.tabela.insert(
                "",
                tk.END,
                values=(
                    ticket.veiculo.placa,
                    ticket.veiculo.modelo,
                    ticket.veiculo.tipo,
                    ticket.vaga.numero,
                    ticket.entrada.strftime("%H:%M:%S")
                )
            )

        # LIMPAR HISTÓRICO
        for item in self.tabela_historico.get_children():
            self.tabela_historico.delete(item)

        # LISTAR HISTÓRICO
        for ticket in self.estacionamento.historico:

            self.tabela_historico.insert(
                "",
                tk.END,
                values=(
                    ticket.veiculo.placa,
                    ticket.saida.strftime("%H:%M:%S"),
                    f"R$ {ticket.valor:.2f}",
                    ticket.forma_pagamento
                )
            )

        # ATUALIZAR INFORMAÇÕES
        vagas = self.estacionamento.vagas

        livres = sum(1 for vaga in vagas if vaga.livre)

        self.label_vagas.config(
            text=f"Vagas disponíveis: {livres}"
        )

        self.label_arrecadado.config(
            text=f"Total arrecadado: R$ {self.estacionamento.arrecadado:.2f}"
        )


# ==========================================
# EXECUTAR PROGRAMA
# ==========================================

janela = tk.Tk()

app = InterfaceEstacionamento(janela)

janela.mainloop()
