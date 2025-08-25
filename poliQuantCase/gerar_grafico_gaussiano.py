import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

def plot_zscore_distribution():
    """
    Carrega os Z-Scores, filtra os pontos de entrada da estratégia
    e plota um histograma com uma curva de densidade (Gaussiana).
    """
    print("[1/3] Carregando o arquivo 'zscores.csv'...")
    try:
        df_zscores = pd.read_csv('zscores.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("ERRO: O arquivo 'zscores.csv' não foi encontrado.")
        print("Por favor, execute o código que gera os Z-Scores primeiro.")
        return

    print("[2/3] Filtrando os Z-Scores que geraram sinais de entrada (compra)...")
    
    ZSCORE_THRESHOLD_LOWER = -2.0
    
    # Transforma o DataFrame de formato largo para longo para analisar todos os Z-scores juntos
    zscores_long = df_zscores.melt(var_name='Ticker', value_name='ZScore')
    
    # Filtra apenas os Z-Scores que ativariam uma compra
    entry_zscores = zscores_long.dropna()
    entry_zscores = entry_zscores[entry_zscores['ZScore'] < ZSCORE_THRESHOLD_LOWER]
    
    if entry_zscores.empty:
        print("Nenhum Z-Score de entrada encontrado com o threshold <= -2.0.")
        return
        
    print(f"Total de {len(entry_zscores)} pontos de entrada encontrados.")

    print("[3/3] Gerando o gráfico da distribuição...")
    
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(12, 7))
    
    # Plota o histograma e a curva de densidade estimada (KDE)
    sns.histplot(entry_zscores['ZScore'], kde=True, stat="density", linewidth=0.5, bins=50, label='Distribuição dos Sinais')
    
    # Calcula os parâmetros da distribuição e plota a curva normal teórica por cima
    mu, std = norm.fit(entry_zscores['ZScore'])
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2, linestyle='--', label='Curva Normal Teórica')
    
    # Formatação do Gráfico
    plt.title('Distribuição dos Z-Scores de Entrada (Sinais de Compra)', fontsize=16, fontweight='bold')
    plt.xlabel('Valor do Z-Score', fontsize=12)
    plt.ylabel('Densidade de Frequência', fontsize=12)
    
    # Adiciona uma linha vertical no ponto do threshold
    plt.axvline(ZSCORE_THRESHOLD_LOWER, color='red', linestyle=':', linewidth=2.5, label=f'Threshold de Compra ({ZSCORE_THRESHOLD_LOWER})')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('distribuicao_zscores_entrada.png', dpi=300)
    
    print("\nGráfico 'distribuicao_zscores_entrada.png' salvo com sucesso!")


if __name__ == '__main__':
    plot_zscore_distribution()
