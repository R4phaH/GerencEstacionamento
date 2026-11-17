import math
import tkinter as tk
from tkinter import ttk, messagebox


class Veiculo:

    TARIFA_HORA = {
        "Carro" : 5.0,
        "Moto" : 3.0,
    }


    def __init__(self, placa, modelo, tipo):
        self.placa = placa.strip().upper()
        self.modelo = modelo.strip()
        self.tipo = tipo.strip().capitalize()


        if self.tipo not in self.TARIFA_HORA:
            raise ValueError(f"Tipo de veículo inválido: {self.tipo} ou não autorizado.")


    def tarifa_hora(self):
        return self.TARIFA_HORA[self.tipo]

class Vaga:
    def __init__(self, numero):
        self.numero = numero
        self.veiculo = None #vaga livre

        def livre(self): #vaga livre
            return self.veiculo is None

        def ocupada(self): #vaga ocupada 
            return self.veiculo is not None

        