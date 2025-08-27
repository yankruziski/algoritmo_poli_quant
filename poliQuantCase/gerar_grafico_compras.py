import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_buy_distribution():
    """
    Carrega os sinais de trade e plota a distribuição dos Z-Scores de compra.
    """
    print("[1/3] Carregando o arquivo 'trade_signals.csv'...")
    try:
        df_signals = pd.read_csv('trade_signals.csv')
    except FileNotFoundError:
        print("ERRO: O arquivo 'trade_signals.csv' não foi encontrado.")
        print("Execute primeiro o backtest para gerar os sinais.")
        return

    print("[2/3] Analisando distribuição dos Z-Scores de compra...")
    
    # Filtra apenas sinais de compra
    buy_signals = df_signals[df_signals['Signal'] == 'Buy']
    print(f"Total de sinais de compra: {len(buy_signals)}")
    
    print("[3/3] Gerando o gráfico de distribuição de compras...")
    
    # Configura o estilo do gráfico
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plota distribuição dos sinais de compra
    sns.histplot(data=buy_signals, x='ZScore', kde=True, ax=ax, 
                stat="density", color='green', alpha=0.6)
    ax.axvline(x=-2.0, color='r', linestyle='--', 
               label='Threshold de Compra (-2.0)')
    ax.set_title('Distribuição dos Z-Scores - Sinais de Compra')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('distribuicao_zscores_compras.png', dpi=300)
    print("\nGráfico 'distribuicao_zscores_compras.png' salvo com sucesso!")

if __name__ == '__main__':
    plot_buy_distribution()