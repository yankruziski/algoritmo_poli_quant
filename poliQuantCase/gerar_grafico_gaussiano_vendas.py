import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

def plot_zscore_distribution_exit():
    """
    Carrega os Z-Scores, filtra os pontos de saída da estratégia
    e plota um histograma com uma curva de densidade (Gaussiana).
    """
    print("[1/3] Carregando o arquivo 'zscores.csv'...")
    try:
        df_zscores = pd.read_csv('zscores.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("ERRO: O arquivo 'zscores.csv' não foi encontrado.")
        print("Por favor, execute o código que gera os Z-Scores primeiro.")
        return

    print("[2/3] Filtrando os Z-Scores que geraram sinais de saída (venda)...")
    
    ZSCORE_THRESHOLD_UPPER = 0.0  # Threshold para saída (venda)
    
    # Transforma o DataFrame de formato largo para longo para analisar todos os Z-scores juntos
    zscores_long = df_zscores.melt(var_name='Ticker', value_name='ZScore')
    
    # Filtra apenas os Z-Scores que ativariam uma venda
    exit_zscores = zscores_long.dropna()
    exit_zscores = exit_zscores[exit_zscores['ZScore'] > ZSCORE_THRESHOLD_UPPER]
    
    if exit_zscores.empty:
        print("Nenhum Z-Score de saída encontrado com o threshold >= 0.0.")
        return
        
    print(f"Total de {len(exit_zscores)} pontos de saída encontrados.")

    print("[3/3] Gerando o gráfico da distribuição...")
    
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(12, 7))
    
    # Plota o histograma e a curva de densidade estimada (KDE)
    sns.histplot(exit_zscores['ZScore'], kde=True, stat="density", linewidth=0.5, bins=50, label='Distribuição dos Sinais')
    
    # Calcula os parâmetros da distribuição e plota a curva normal teórica por cima
    mu, std = norm.fit(exit_zscores['ZScore'])
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2, linestyle='--', label='Curva Normal Teórica')
    
    # Formatação do Gráfico
    plt.title('Distribuição dos Z-Scores de Saída (Sinais de Venda)', fontsize=16, fontweight='bold')
    plt.xlabel('Valor do Z-Score', fontsize=12)
    plt.ylabel('Densidade de Frequência', fontsize=12)
    
    # Adiciona uma linha vertical no ponto do threshold
    plt.axvline(ZSCORE_THRESHOLD_UPPER, color='green', linestyle=':', linewidth=2.5, label=f'Threshold de Venda ({ZSCORE_THRESHOLD_UPPER})')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('distribuicao_zscores_saida.png', dpi=300)
    
    print("\nGráfico 'distribuicao_zscores_saida.png' salvo com sucesso!")


def plot_sell_distribution():
    """
    Carrega os sinais de trade e plota a distribuição dos Z-Scores de venda.
    """
    print("[1/3] Carregando o arquivo 'trade_signals.csv'...")
    try:
        df_signals = pd.read_csv('trade_signals.csv')
    except FileNotFoundError:
        print("ERRO: O arquivo 'trade_signals.csv' não foi encontrado.")
        print("Execute primeiro o backtest para gerar os sinais.")
        return

    print("[2/3] Analisando distribuição dos Z-Scores de venda...")
    
    # Filtra apenas sinais de venda
    sell_signals = df_signals[df_signals['Signal'] == 'Sell']
    print(f"Total de sinais de venda: {len(sell_signals)}")
    
    print("[3/3] Gerando o gráfico de distribuição de vendas...")
    
    # Configura o estilo do gráfico
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plota distribuição dos sinais de venda
    sns.histplot(data=sell_signals, x='ZScore', kde=True, ax=ax, 
                stat="density", color='red', alpha=0.6)
    ax.axvline(x=2.0, color='r', linestyle='--', 
               label='Threshold de Venda (+2.0)')
    ax.set_title('Distribuição dos Z-Scores - Sinais de Venda')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('distribuicao_zscores_vendas.png', dpi=300)
    print("\nGráfico 'distribuicao_zscores_vendas.png' salvo com sucesso!")


if __name__ == '__main__':
    plot_zscore_distribution_exit()
    plot_sell_distribution()