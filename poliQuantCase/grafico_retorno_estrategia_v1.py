import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def plotar_grafico_retorno():
    """
    Carrega os resultados de um backtest e plota a curva de capital
    comparando a estratégia com o IBOV.
    """
    print("\n--- Gerando o Gráfico de Retorno da Estratégia V1 ---")
    try:
        # Carrega o histórico do portfólio que acabamos de salvar
        df_portfolio = pd.read_csv('portfolio_history_v1.csv', index_col='Date', parse_dates=True)
        # Carrega os dados originais para pegar a série do IBOV
        df_precos = pd.read_csv('dados_tratados.csv', index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("ERRO: Arquivos de resultado não encontrados. Execute o Passo 1 primeiro.")
        return

    # 1. Normalizar os dados para uma base 100
    df_portfolio['Performance'] = (df_portfolio['Portfolio_Value'] / df_portfolio['Portfolio_Value'].iloc[0]) * 100
    df_precos['IBOV_Performance'] = (df_precos['IBOV'] / df_precos['IBOV'].iloc[0]) * 100

    # 2. Configurar o Gráfico
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    # 3. Plotar as Linhas de Performance
    ax.plot(df_portfolio.index, df_portfolio['Performance'], 
            label='Estratégia Reversão à Média (V1)', 
            color='royalblue', 
            linewidth=2)

    ax.plot(df_precos.index, df_precos['IBOV_Performance'], 
            label='IBOV (Benchmark)', 
            color='darkorange', 
            linewidth=2, 
            linestyle='--')

    # 4. Formatação e Títulos
    ax.set_title('Curva de Capital Comparativa da Estratégia V1 (2010-2024)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Crescimento do Capital (Base 100)', fontsize=12)
    ax.legend(fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 5. Salvar o Gráfico
    plt.savefig('grafico_retorno_estrategia_v1.png', dpi=300)
    print("\nGráfico 'grafico_retorno_estrategia_v1.png' salvo com sucesso!")


if __name__ == '__main__':
    plotar_grafico_retorno()



def run_successful_backtest_and_plot():
    """
    Executa o backtest da primeira estratégia (v1, bem-sucedida) e gera
    o gráfico de curva de capital.
    """
    print("--- GERANDO GRÁFICO PARA A ESTRATÉGIA DE SUCESSO (V1) ---")

    # ETAPA 1: CARREGAR OS DADOS NECESSÁRIOS
    # =======================================
    print("\n[ETAPA 1/3] Carregando dados pré-tratados e sinais...")
    try:
        df_precos = pd.read_csv('dados_tratados.csv', index_col='Date', parse_dates=True)
        # Os sinais originais usavam 'Buy' e 'Sell' para os extremos
        df_zscores = pd.read_csv('zscores.csv', index_col='Date', parse_dates=True)
        tickers_acoes = [col for col in df_zscores.columns if col != 'IBOV']
        df_sinais = pd.DataFrame('Hold', index=df_zscores.index, columns=tickers_acoes)
        df_sinais[df_zscores < -2.0] = 'Buy'
        df_sinais[df_zscores > 2.0] = 'Sell'
        
    except FileNotFoundError:
        print("ERRO: Certifique-se que os arquivos 'dados_tratados.csv' e 'zscores.csv' estão na pasta.")
        return
    print("Dados carregados.")

    # ETAPA 2: EXECUTAR A SIMULAÇÃO DO BACKTEST (ESTRATÉGIA V1)
    # =========================================================
    print("\n[ETAPA 2/3] Executando a simulação da estratégia original...")
    
    INITIAL_CAPITAL = 1000000.00
    POSITION_SIZE = 50000.00
    
    cash = INITIAL_CAPITAL
    positions = {ticker: 0 for ticker in tickers_acoes} # Armazena a quantidade de ações
    portfolio_history = []

    for date, row in df_precos.iterrows():
        current_positions_value = sum(positions[ticker] * row[ticker] for ticker in tickers_acoes if positions[ticker] > 0)
        total_portfolio_value = cash + current_positions_value
        portfolio_history.append({'Date': date, 'Portfolio_Value': total_portfolio_value})

        sinais_do_dia = df_sinais.loc[date]
        for ticker in tickers_acoes:
            signal = sinais_do_dia[ticker]
            current_price = row[ticker]
            
            if signal == 'Sell' and positions[ticker] > 0:
                cash += positions[ticker] * current_price
                positions[ticker] = 0
            elif signal == 'Buy' and positions[ticker] == 0 and cash >= POSITION_SIZE:
                positions[ticker] = POSITION_SIZE / current_price
                cash -= POSITION_SIZE
                
    df_portfolio = pd.DataFrame(portfolio_history).set_index('Date')
    print("Simulação concluída.")

    # ETAPA 3: GERAR O GRÁFICO DE RETORNO
    # ======================================
    print("\n[ETAPA 3/3] Gerando o gráfico da Curva de Capital...")
    
    df_portfolio['Portfolio_Return_Base100'] = (df_portfolio['Portfolio_Value'] / INITIAL_CAPITAL) * 100
    df_precos['IBOV_Return_Base100'] = (df_precos['IBOV'] / df_precos['IBOV'].iloc[0]) * 100

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(df_portfolio.index, df_portfolio['Portfolio_Return_Base100'], label='Estratégia Reversão à Média (V1)', color='royalblue', linewidth=2)
    ax.plot(df_precos.index, df_precos['IBOV_Return_Base100'], label='IBOV (Benchmark)', color='darkorange', linewidth=2, linestyle='--')

    ax.set_title('Curva de Capital da Estratégia V1 vs. IBOV (2010-2024)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Crescimento do Capital (Base 100)', fontsize=12)
    ax.legend(fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig('equity_curve_v1_sucesso.png', dpi=300)
    print("Gráfico 'equity_curve_v1_sucesso.png' salvo com sucesso!")

if __name__ == '__main__':
    run_successful_backtest_and_plot()


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def run_successful_backtest_and_plot():
    """
    Executa o backtest da primeira estratégia (v1, bem-sucedida) e gera
    o gráfico de curva de capital.
    """
    print("--- GERANDO GRÁFICO PARA A ESTRATÉGIA DE SUCESSO (V1) ---")

    # ETAPA 1: CARREGAR OS DADOS NECESSÁRIOS
    print("\n[ETAPA 1/3] Carregando dados pré-tratados e sinais...")
    try:
        df_precos = pd.read_csv('dados_tratados.csv', index_col='Date', parse_dates=True)
        df_zscores = pd.read_csv('zscores.csv', index_col='Date', parse_dates=True)
        tickers_acoes = [col for col in df_zscores.columns if col != 'IBOV']
        
        # Recriar os sinais para a estratégia v1
        df_sinais = pd.DataFrame('Hold', index=df_zscores.index, columns=tickers_acoes)
        df_sinais[df_zscores < -2.0] = 'Buy'
        df_sinais[df_zscores > 2.0] = 'Sell'
        
    except FileNotFoundError:
        print("ERRO: Certifique-se que os arquivos 'dados_tratados.csv' e 'zscores.csv' estão na pasta.")
        return
    print("Dados carregados.")

    # ETAPA 2: EXECUTAR A SIMULAÇÃO DO BACKTEST (ESTRATÉGIA V1)
    print("\n[ETAPA 2/3] Executando a simulação da estratégia original...")
    
    INITIAL_CAPITAL = 1000000.00
    POSITION_SIZE = 50000.00
    
    cash = INITIAL_CAPITAL
    positions = {ticker: 0 for ticker in tickers_acoes}
    portfolio_history = []

    for date, row in df_precos.iterrows():
        # Assegurar que a data existe em ambos os dataframes
        if date not in df_sinais.index:
            continue
            
        current_positions_value = sum(positions[ticker] * row[ticker] for ticker in tickers_acoes if positions[ticker] > 0)
        total_portfolio_value = cash + current_positions_value
        portfolio_history.append({'Date': date, 'Portfolio_Value': total_portfolio_value})

        sinais_do_dia = df_sinais.loc[date]
        for ticker in tickers_acoes:
            signal = sinais_do_dia[ticker]
            current_price = row[ticker]
            
            if not np.isnan(current_price): # Checagem extra de segurança
                if signal == 'Sell' and positions[ticker] > 0:
                    cash += positions[ticker] * current_price
                    positions[ticker] = 0
                elif signal == 'Buy' and positions[ticker] == 0 and cash >= POSITION_SIZE:
                    positions[ticker] = POSITION_SIZE / current_price
                    cash -= POSITION_SIZE
                
    df_portfolio = pd.DataFrame(portfolio_history).set_index('Date')
    print("Simulação concluída.")

    # ETAPA 3: GERAR O GRÁFICO DE RETORNO
    print("\n[ETAPA 3/3] Gerando o gráfico da Curva de Capital...")
    
    df_portfolio['Portfolio_Return_Base100'] = (df_portfolio['Portfolio_Value'] / INITIAL_CAPITAL) * 100
    df_precos['IBOV_Return_Base100'] = (df_precos['IBOV'] / df_precos['IBOV'].iloc[0]) * 100

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(df_portfolio.index, df_portfolio['Portfolio_Return_Base100'], label='Estratégia Reversão à Média (V1)', color='royalblue', linewidth=2)
    ax.plot(df_precos.index, df_precos['IBOV_Return_Base100'], label='IBOV (Benchmark)', color='darkorange', linewidth=2, linestyle='--')

    ax.set_title('Curva de Capital da Estratégia V1 vs. IBOV (2010-2024)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Crescimento do Capital (Base 100)', fontsize=12)
    ax.legend(fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig('equity_curve_v1_sucesso.png', dpi=300)
    print("Gráfico 'equity_curve_v1_sucesso.png' salvo com sucesso!")

if __name__ == '__main__':
    run_successful_backtest_and_plot()