import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# Carrega os preços
df_precos = pd.read_csv('precos_b3_202010-2024.csv', index_col='Date', parse_dates=True)

# Calcula z-score para cada ativo (exceto IBOV)
window = 20  # janela de 20 dias, ajuste se necessário
tickers = [col for col in df_precos.columns if col != 'IBOV']

df_zscores = pd.DataFrame(index=df_precos.index, columns=tickers)

for ticker in tickers:
    rolling_mean = df_precos[ticker].rolling(window).mean()
    rolling_std = df_precos[ticker].rolling(window).std()
    df_zscores[ticker] = (df_precos[ticker] - rolling_mean) / rolling_std

# Salva o resultado
df_zscores.to_csv('zscores.csv')
print("Arquivo 'zscores.csv' gerado com sucesso!")

def carregar_e_preparar_dados():
    """
    ETAPA 1: Carrega os dados dos arquivos CSV, trata e prepara os sinais
    para a Estratégia V1.
    """
    print("[ETAPA 1/3] Carregando e preparando os dados...")
    try:
        df_precos = pd.read_csv('precos_b3_202010-2024.csv', index_col='Date', parse_dates=True)
        df_zscores = pd.read_csv('zscores.csv', index_col='Date', parse_dates=True)  # ajuste se necessário
    except FileNotFoundError:
        print("ERRO CRÍTICO: 'precos_b3_202010-2024.csv' ou 'zscores.csv' não encontrados.")
        print("Certifique-se de que os arquivos gerados nas etapas anteriores estão na mesma pasta.")
        return None, None

    tickers_acoes = [col for col in df_precos.columns if col != 'IBOV']
    
    # Gera os sinais para a Estratégia V1 (compra em < -2.0, venda em > +2.0)
    df_sinais = pd.DataFrame('Hold', index=df_zscores.index, columns=tickers_acoes)
    df_sinais[df_zscores < -2.0] = 'Buy'
    df_sinais[df_zscores > 2.0] = 'Sell'
    
    print("Dados e sinais carregados com sucesso.")
    return df_precos, df_sinais

def rodar_backtest_v1(df_precos, df_sinais):
    """
    ETAPA 2: Executa a simulação do backtest para a Estratégia V1.
    """
    print("\n[ETAPA 2/3] Executando a simulação do backtest...")
    
    INITIAL_CAPITAL = 1000000.00
    POSITION_SIZE = 50000.00
    
    cash = INITIAL_CAPITAL
    tickers_acoes = df_sinais.columns
    positions = {ticker: 0 for ticker in tickers_acoes}
    portfolio_history = []

    for date, row in df_precos.iterrows():
        # Garante que a data atual existe no DataFrame de sinais
        if date not in df_sinais.index:
            continue
            
        # Calcula o valor das posições e registra o valor total do portfólio
        current_positions_value = sum(positions[ticker] * row[ticker] for ticker in tickers_acoes if positions[ticker] > 0 and not np.isnan(row[ticker]))
        total_portfolio_value = cash + current_positions_value
        portfolio_history.append({'Date': date, 'Portfolio_Value': total_portfolio_value})

        # Executa as ordens com base nos sinais do dia
        sinais_do_dia = df_sinais.loc[date]
        for ticker in tickers_acoes:
            signal = sinais_do_dia[ticker]
            current_price = row[ticker]
            
            # Checagem de segurança para evitar operar com preços nulos
            if not np.isnan(current_price):
                # Lógica de Venda (saída da posição)
                if signal == 'Sell' and positions[ticker] > 0:
                    cash += positions[ticker] * current_price
                    positions[ticker] = 0
                # Lógica de Compra (entrada na posição)
                elif signal == 'Buy' and positions[ticker] == 0 and cash >= POSITION_SIZE:
                    positions[ticker] = POSITION_SIZE / current_price
                    cash -= POSITION_SIZE
                
    df_portfolio = pd.DataFrame(portfolio_history).set_index('Date')
    print("Simulação concluída.")
    return df_portfolio

def plotar_grafico_final(df_portfolio, df_precos):
    """
    ETAPA 3: Usa os resultados do backtest para gerar e salvar o gráfico final.
    """
    print("\n[ETAPA 3/3] Gerando o gráfico final da Curva de Capital...")
    
    # Normaliza os dados para uma base 100 para facilitar a comparação
    df_portfolio['Performance'] = (df_portfolio['Portfolio_Value'] / df_portfolio['Portfolio_Value'].iloc[0]) * 100
    df_precos['IBOV_Performance'] = (df_precos['IBOV'] / df_precos['IBOV'].iloc[0]) * 100

    # Configurações de estilo e tamanho do gráfico
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plotagem das linhas de performance
    ax.plot(df_portfolio.index, df_portfolio['Performance'], label='Estratégia Reversão à Média (V1)', color='royalblue', linewidth=2)
    ax.plot(df_precos.index, df_precos['IBOV_Performance'], label='IBOV (Benchmark)', color='darkorange', linewidth=2, linestyle='--')

    # Títulos, legendas e formatação
    ax.set_title('Curva de Capital da Estratégia V1 vs. IBOV (2010-2024)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Crescimento do Capital (Base 100)', fontsize=12)
    ax.legend(fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Salva a imagem final
    plt.savefig('grafico_final_estrategia_v1.png', dpi=300)
    print("Gráfico 'grafico_final_estrategia_v1.png' salvo com sucesso!")


# Bloco de execução principal
if __name__ == '__main__':
    # Chama as funções na ordem correta
    precos, sinais = carregar_e_preparar_dados()
    
    # Apenas continua se os dados foram carregados corretamente
    if precos is not None and sinais is not None:
        portfolio_resultado = rodar_backtest_v1(precos, sinais)
        plotar_grafico_final(portfolio_resultado, precos)