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