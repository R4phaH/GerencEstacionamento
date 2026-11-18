from datetime import datetime
import math
import tkinter as tk
from tkinter import ttk, messagebox


class Veiculo:

    TARIFA_HORA = {"Carro": 5.0,  "Moto": 3.0,}


    def __init__(self, placa, modelo, tipo):
        self.placa = placa.strip().upper()
        self.modelo = modelo.strip()
        self.tipo = tipo.strip().capitalize()

        if self.tipo not in self.TARIFA_HORA:
            raise ValueError(f"Tipo de veículo inválido: {self.tipo} ou não autorizado.") 


    def tarifa_hora(self):
        return self.TARIFA_HORA[self.tipo]

    

class Vaga:
    def __init__(self, numero, veiculo=None):
        self.numero = numero
        self.veiculo = veiculo

    # Consultam o estado da vaga
    @property
    def livre(self):
        return self.veiculo is None

    @property
    def ocupada(self):
        return self.veiculo is not None

    # Alteram o estado da vaga
    def ocupar(self, veiculo):
        self.veiculo = veiculo

    def liberar(self):
        self.veiculo = None

class Ticket:
    #estadia do veiculo -> vai ligar um veiculo a uma vaga 
    TOLERANCIA_MINUTOS = 15 
    DIARIA_MAX = 40  
    MINUTOS_POR_DIA = 24 * 60

    def __init__(self, veiculo, vaga): #estou definindo a entrada do veiculo na vaga
        self.veiculo = veiculo
        self.vaga = vaga 
        self.entrada = datetime.now()
        self.saida = None
        self.valor = 0.0
        self.forma_pagamento = None

    def minutos_estacionado(self, ate=None):
        ate = ate or datetime.now()                        #até quando contar
        return (ate - self.entrada).total_seconds() / 60

    def calcular_valor(self, ate=None):
        minutos = self.minutos_estacionado(ate)            #quantos munutos o veiculo ficou estacionado

        if minutos < 0:
            raise ValueError("A data de saída não pode ser anterior à entrada.") 
        
        if minutos <= self.TOLERANCIA_MINUTOS:
            return 0.0        
        
        horas = math.ceil(minutos / 60)  #minutos em horas arredondando para cima

        valor_horas = horas * self.veiculo.tarifa_hora() #valor das horas multiplicado pela tarifa do veiculo
        
        dias = math.ceil(minutos / self.MINUTOS_DIA) #limite de horas para o valor máximo da diária
        limite_diaria = dias * self.DIARIA_MAX

        return min(valor_horas, limite_diaria)  #retorna o valor minimo entre o valor das horas e o limite da diaria


class Estacionamento:
    FORMAS_PAGAMENTO = {
        "dinheiro": "Dinheiro",
        "pix": "Pix",
        "cartão de crédito": "Cartão de crédito",
        "cartão de débito": "Cartão de débito"
    }
    def __init__(self, total_vagas = 10):
        if (
            not isinstance(total_vagas, int)
            or isinstance(total_vagas, bool)
            or total_vagas <= 0
        ):
            raise ValueError("A quantidade de vagas deve ser um inteiro positivo.")
        
        self.vagas = [Vaga(numero = i + 1) for i in range(total_vagas)]
        self.tickets_abertos = {} #todas as casas comecam vazias - dicionario de tickets abertos - onde os carros ficam que entraram e ainda nao sairam
        self.historico = [] #ja saiu do estacionamento - historico de tickets fechados
        self.arrecadado = 0.0 

    def primeira_vaga_livre(self): #ele percorre a vaga e se ele nao achar nenhuma vaga livre ele retorna None(lotado)
        for vaga in self.vagas:
            if vaga.livre:
                return vaga
        return None

    def registrar_entrada(self, veiculo): #quando um carro entra no estacionamento 

        if not isinstance(veiculo, Veiculo):
            raise ValueError("Veículo inválido.")

        
        if veiculo.placa in self.tickets_abertos:
            raise ValueError("Este veículo já está no estacionamento.")
        
        vaga = self.primeira_vaga_livre()
        if vaga is None:
            raise ValueError("Estacionamento lotado.")
        
        vaga.ocupar(veiculo)
        ticket = Ticket(veiculo, vaga)
        self.tickets_abertos[veiculo.placa] = ticket  #placa -> ticket    #associar o ticket ao veículo adicionando no dicionário de tickets abertos
        return ticket
    
    def buscar_ticket(self, placa):
        return self.tickets_abertos.get(placa.strip().upper()) #eu acho o ticket pela placa

    def registrar_saida(self, placa, forma_pagamento):
        placa = placa.strip().upper()

        ticket = self.buscar_ticket(placa)
        if ticket is None:
            raise ValueError("Veículo não encontrado no estacionamento.")

        pagamento = forma_pagamento.strip().lower()
        if pagamento not in self.FORMAS_PAGAMENTO:
            raise ValueError("Forma de pagamento inválida.")
        
        ticket.saida = datetime.now() #saida do veiculo(obviamente a hora que ele saiu)

        ticket.valor = ticket.calcular_valor(ticket.saida) #calcula o valor do ticket

        ticket.forma_pagamento = self.FORMAS_PAGAMENTO[pagamento] #forma de pagamento do ticket

        ticket.vaga.liberar() #vaga liberada


        #atualizar os registros do estacionamento
        del self.tickets_abertos[placa]
        self.historico.append(ticket) #Remove o ticket do dicionário de tickets abertos e adiciona ao histórico

        #arrecadação
        self.arrecadado += ticket.valor

        return ticket