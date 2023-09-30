import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import numpy as np


class DadosSinaisVitais:
    def __init__(self, path):
        self.dados = self.ler_dados(path)
        if self.dados:
            self.preprocessar_dados()
        else:
            print("Erro: Nenhum dado encontrado no arquivo.")

    def ler_dados(self, path):
        try:
            with open(path, "r") as arquivo:
                linhas = arquivo.readlines()
                dados = []
                for linha in linhas:
                    valores = linha.strip().split()
                    if len(valores) == 4:
                        dados.append(valores)
                    else:
                        print(f"Erro: Linha inválida encontrada: {linha}")
                return dados
        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado no caminho '{path}'.")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
        return None

    def preprocessar_dados(self):
        for i in range(len(self.dados) - 2):
            self.preprocessar_valor(
                1, i
            )  # Índice correspondente a 'BATIMENTO CARDIACO'
            self.preprocessar_valor(2, i)  # Índice correspondente a 'PRESSAO'
            self.preprocessar_valor(
                3, i
            )  # Índice correspondente a 'TEMPERATURA CORPORAL'

    def preprocessar_valor(self, indice, linha):
        try:
            valor = float(self.dados[linha][indice])
            if valor < 0 or valor > self.limite_superior(indice):
                self.dados[linha][indice] = self.calcular_media(indice, linha)
        except (IndexError, ValueError):
            print(f"Erro: Valor inválido na linha {linha + 1}, índice {indice}.")

    def calcular_media(self, indice, linha):
        valor_anterior = float(self.dados[linha - 1][indice])
        valor_posterior = float(self.dados[linha + 1][indice])
        return (valor_anterior + valor_posterior) / 2

    def limite_superior(self, indice):
        if indice == 1:  # 'BATIMENTO CARDIACO'
            return 100
        elif indice == 2:  # 'PRESSAO'
            return 20
        elif indice == 3:  # 'TEMPERATURA CORPORAL'
            return 40

    def criar_dataframe(self):
        colunas = [
            "HORA",
            "BATIMENTO CARDIACO",
            "PRESSAO ARTERIAL",
            "TEMPERATURA CORPORAL",
        ]
        return pd.DataFrame(self.dados, columns=colunas)


class EstatisticasSinaisVitais:
    def __init__(self, dados):
        self.dados = dados

    def calcular_estatisticas(self, chave):
        valores = self.dados[chave].astype(float)
        media = np.mean(valores)
        maximo = np.max(valores)
        minimo = np.min(valores)
        return media, maximo, minimo

    def gerar_histograma(self, chave):
        valores = self.dados[chave].astype(float)
        plt.hist(valores)
        plt.xlabel(chave)
        plt.ylabel("FREQUENCIA")
        plt.show()


class VisualizadorSinaisVitais:
    def __init__(self, dados):
        self.dados = dados
        self.chaves = ["BATIMENTO CARDIACO", "PRESSAO ARTERIAL", "TEMPERATURA CORPORAL"]
        self.indice = 0
        self.root = tk.Tk()
        self.root.title("Visualização Gráfica")
        style = ThemedStyle(self.root)
        style.set_theme("equilux")

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.atualizar_grafico()

        self.progress_bar = ttk.Progressbar(
            self.root, orient="horizontal", length=200, mode="determinate"
        )
        self.progress_bar.pack(side=tk.BOTTOM, pady=10)

        button_forward = ttk.Button(self.root, text="Próximo", command=self.avancar)
        button_forward.pack(side=tk.BOTTOM, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.fechar_janela)
        self.root.mainloop()

    def atualizar_grafico(self):
        chave = self.chaves[self.indice]
        valores = self.dados[chave].astype(float)
        self.ax.clear()
        self.ax.hist(valores, bins=20, color="skyblue", alpha=0.9)
        self.ax.set_xlabel(chave)
        self.ax.set_ylabel("FREQUENCIA")
        self.ax.set_title(
            f"{chave} (Média: {np.mean(valores):.2f}, Máximo: {np.max(valores):.2f}, Mínimo: {np.min(valores):.2f})"
        )
        self.canvas.draw()

    def avancar(self):
        self.indice = (self.indice + 1) % len(self.chaves)
        self.atualizar_grafico()
        progresso = (self.indice + 1) * 100 / len(self.chaves)
        self.progress_bar["value"] = progresso

    def fechar_janela(self):
        chave = self.chaves[self.indice]
        valores = self.dados[chave].astype(float)
        self.root.destroy()
        sys.exit()


def imprimir_dados(dados):
    tamanho_amostra = len(dados)
    for chave in ["BATIMENTO CARDIACO", "PRESSAO ARTERIAL", "TEMPERATURA CORPORAL"]:
        valores = dados[chave].astype(float)
        media = np.mean(valores)
        maximo = np.max(valores)
        minimo = np.min(valores)

        print("\n\n*************************************************")
        print(f"{chave}")
        print("*************************************************")
        print(f"Tamanho da amostra: {tamanho_amostra}")
        print(f"Média: {media:.2f}")
        print(f"Máximo: {maximo:.2f}")
        print(f"Mínimo: {minimo:.2f}")


def main():
    path = "dados.txt"
    dados_sinais_vitais = DadosSinaisVitais(path)
    if dados_sinais_vitais.dados:
        dataframe = dados_sinais_vitais.criar_dataframe()

        correlacao = dataframe.corr()
        print(
            "\n\n**************************************************************************************************"
        )
        print("CORRELAÇÃO ENTRE OS PARÂMETROS")
        print(
            "**************************************************************************************************"
        )
        print(correlacao)
        print("\n\n")

        # Imprimir estatísticas dos dados
        imprimir_dados(dataframe)

        # Abrir a janela de visualização
        VisualizadorSinaisVitais(dataframe)


if __name__ == "__main__":
    main()
