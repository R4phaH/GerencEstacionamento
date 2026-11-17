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
    DIARIA_MAX = 24 * 60  # 24 horas - 40reais

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

        if minutos <= self.TOLERANCIA_MINUTOS:
            return 0.0
        
        horas = math.ceil(minutos / 60)  #minutos em horas arredondando para cima
        horas = min(horas, self.DIARIA_MAX / 60)  #limite de horas para o valor máximo da diária
        return horas * self.veiculo.tarifa_hora()


class Estacionamento:

    def __init__(self, total_vagas = 10):
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

        ticket = self.buscar_ticket(placa)
        if ticket is None:
            raise ValueError("Veículo não encontrado no estacionamento.")
        
        ticket.saida = datetime.now() #saida do veiculo(obviamente a hora que ele saiu)
        ticket.valor = ticket.calcular_valor()
        ticket.forma_pagamento = forma_pagamento

        ticket.vaga.liberar() #vaga liberada

        
        del self.tickets_abertos[placa.strip().upper()]
        self.historico.append(ticket) #Remove o ticket do dicionário de tickets abertos e adiciona ao histórico

        #arrecadação
        self.arrecadado += ticket.valor

        return ticket