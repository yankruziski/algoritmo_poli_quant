# Importação das bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

def carregar_dados():
    """ETAPA 1: Carrega e trata os dados iniciais"""
    print("\n[ETAPA 1/5] Carregando e tratando os dados...")
    try:
        df_acoes = pd.read_csv('precos_b3_202010-2024.csv')
        df_ibov = pd.read_csv('ibov_2010_2024.csv')
    except FileNotFoundError:
        print("ERRO: Certifique-se que os arquivos 'precos_b3_202010-2024.csv' e 'ibov_2010_2024.csv' estão na mesma pasta.")
        return None, None

    # Tratamento do IBOV
    if df_ibov.iloc[0]['Close'] == '^BVSP':
        df_ibov = df_ibov.iloc[1:].copy()
    df_ibov['Date'] = pd.to_datetime(df_ibov['Date'])
    df_ibov['Close'] = pd.to_numeric(df_ibov['Close'], errors='coerce')
    df_ibov.rename(columns={'Close': 'IBOV'}, inplace=True)
    df_ibov.set_index('Date', inplace=True)
    df_ibov.dropna(inplace=True)

    # Tratamento das Ações
    df_acoes['Date'] = pd.to_datetime(df_acoes['Date'])
    df_acoes.set_index('Date', inplace=True)

    # Filtragem e unificação
    df_acoes_filtrado = df_acoes.dropna(axis=1)
    df_precos = df_acoes_filtrado.join(df_ibov, how='inner')
    
    print(f"Dados tratados. Universo de backtest: {df_acoes_filtrado.shape[1]} ativos.")
    return df_precos, df_acoes_filtrado.columns

def gerar_sinais(df_precos, tickers_acoes):
    """ETAPA 2: Calcula indicadores e gera sinais"""
    print("\n[ETAPA 2/5] Calculando Z-Scores e gerando sinais...")
    
    ROLLING_WINDOW = 50
    ZSCORE_THRESHOLD_UPPER = 2.0
    ZSCORE_THRESHOLD_LOWER = -2.0
    
    df_zscores = pd.DataFrame(index=df_precos.index)
    trade_signals = []  # Lista para armazenar informações das operações
    
    for ticker in tickers_acoes:
        media_movel = df_precos[ticker].rolling(window=ROLLING_WINDOW).mean()
        desvio_padrao_movel = df_precos[ticker].rolling(window=ROLLING_WINDOW).std()
        df_zscores[ticker] = (df_precos[ticker] - media_movel) / desvio_padrao_movel
        
        # Identifica sinais de compra e venda
        for date in df_zscores.index:
            zscore = df_zscores.loc[date, ticker]
            if pd.notna(zscore):  # Verifica se o Z-score é válido
                if zscore < ZSCORE_THRESHOLD_LOWER:
                    trade_signals.append({
                        'Date': date,
                        'Ticker': ticker,
                        'ZScore': zscore,
                        'Signal': 'Buy',
                        'Price': df_precos.loc[date, ticker]
                    })
                elif zscore > ZSCORE_THRESHOLD_UPPER:
                    trade_signals.append({
                        'Date': date,
                        'Ticker': ticker,
                        'ZScore': zscore,
                        'Signal': 'Sell',
                        'Price': df_precos.loc[date, ticker]
                    })
    
    # Cria DataFrame de sinais
    df_sinais = pd.DataFrame('Hold', index=df_zscores.index, columns=tickers_acoes)
    df_sinais[df_zscores < ZSCORE_THRESHOLD_LOWER] = 'Buy'
    df_sinais[df_zscores > ZSCORE_THRESHOLD_UPPER] = 'Sell'
    
    # Salva Z-scores e sinais em CSV
    df_zscores.to_csv('zscores.csv')
    
    # Salva informações detalhadas das operações
    df_trade_signals = pd.DataFrame(trade_signals)
    if not df_trade_signals.empty:
        df_trade_signals = df_trade_signals.sort_values(['Date', 'Ticker'])
        df_trade_signals.to_csv('trade_signals.csv', index=False)
        print(f"Total de sinais gerados: {len(df_trade_signals)}")
        print(f"Compras: {len(df_trade_signals[df_trade_signals['Signal'] == 'Buy'])}")
        print(f"Vendas: {len(df_trade_signals[df_trade_signals['Signal'] == 'Sell'])}")
    
    print("Sinais de Compra/Venda gerados e salvos em 'trade_signals.csv'")
    return df_sinais

def executar_backtest(df_precos, df_sinais, tickers_acoes):
    """ETAPA 3: Executa simulação do backtest"""
    print("\n[ETAPA 3/5] Executando a simulação de ordens...")
    
    INITIAL_CAPITAL = 1000000.00
    POSITION_SIZE = 50000.00
    
    cash = INITIAL_CAPITAL
    positions = {ticker: 0 for ticker in tickers_acoes}
    portfolio_history = []

    for date, row in df_precos.iterrows():
        current_positions_value = sum(positions[ticker] * row[ticker] for ticker in tickers_acoes)
        total_portfolio_value = cash + current_positions_value
        portfolio_history.append({'Date': date, 'Portfolio_Value': total_portfolio_value})

        sinais_do_dia = df_sinais.loc[date]
        for ticker in tickers_acoes:
            signal = sinais_do_dia[ticker]
            
            if signal == 'Sell' and positions[ticker] > 0:
                sell_price = row[ticker]
                cash += positions[ticker] * sell_price
                positions[ticker] = 0
            elif signal == 'Buy' and positions[ticker] == 0 and cash >= POSITION_SIZE:
                buy_price = row[ticker]
                positions[ticker] = POSITION_SIZE / buy_price
                cash -= POSITION_SIZE
    
    df_portfolio = pd.DataFrame(portfolio_history).set_index('Date')
    print("Simulação concluída.")
    return df_portfolio, INITIAL_CAPITAL

def calcular_metricas(df_portfolio, df_precos, INITIAL_CAPITAL):
    """ETAPA 4: Calcula métricas de performance"""
    print("\n[ETAPA 4/5] Calculando métricas de performance...")
    
    # Prepara retornos
    df_portfolio['Daily_Return'] = df_portfolio['Portfolio_Value'].pct_change()
    df_precos['IBOV_Daily_Return'] = df_precos['IBOV'].pct_change()
    
    # Métricas da Estratégia
    total_return_strategy = (df_portfolio['Portfolio_Value'].iloc[-1] / INITIAL_CAPITAL) - 1
    annual_return_strategy = (1 + total_return_strategy) ** (252 / len(df_portfolio)) - 1
    annual_volatility_strategy = df_portfolio['Daily_Return'].std() * np.sqrt(252)
    sharpe_ratio_strategy = annual_return_strategy / annual_volatility_strategy
    
    # Métricas do IBOV
    total_return_ibov = (df_precos['IBOV'].iloc[-1] / df_precos['IBOV'].iloc[0]) - 1
    annual_return_ibov = (1 + total_return_ibov) ** (252 / len(df_precos)) - 1
    annual_volatility_ibov = df_precos['IBOV_Daily_Return'].std() * np.sqrt(252)
    sharpe_ratio_ibov = annual_return_ibov / annual_volatility_ibov
    
    # Drawdowns
    portfolio_cum_return = (1 + df_portfolio['Daily_Return']).cumprod()
    portfolio_peak = portfolio_cum_return.cummax()
    portfolio_drawdown = (portfolio_cum_return - portfolio_peak) / portfolio_peak
    max_drawdown_strategy = portfolio_drawdown.min()

    ibov_cum_return = (1 + df_precos['IBOV_Daily_Return']).cumprod()
    ibov_peak = ibov_cum_return.cummax()
    ibov_drawdown = (ibov_cum_return - ibov_peak) / ibov_peak
    max_drawdown_ibov = ibov_drawdown.min()
    
    results = {
        "Métrica": ["Rentabilidade Total", "Retorno Anualizado", "Volatilidade Anualizada", 
                   "Índice de Sharpe", "Drawdown Máximo"],
        "Estratégia": [f"{total_return_strategy:.2%}", f"{annual_return_strategy:.2%}", 
                      f"{annual_volatility_strategy:.2%}", f"{sharpe_ratio_strategy:.2f}", 
                      f"{max_drawdown_strategy:.2%}"],
        "IBOV": [f"{total_return_ibov:.2%}", f"{annual_return_ibov:.2%}", 
                 f"{annual_volatility_ibov:.2%}", f"{sharpe_ratio_ibov:.2f}", 
                 f"{max_drawdown_ibov:.2%}"]
    }
    df_results = pd.DataFrame(results)
    print("\n--- MÉTRICAS DE PERFORMANCE ---")
    print(df_results)
    
    return df_results

def plotar_resultados(df_portfolio, df_precos, INITIAL_CAPITAL):
    """ETAPA 5: Gera visualização dos resultados"""
    print("\n[ETAPA 5/5] Gerando gráfico da Curva de Capital...")
    
    df_portfolio['Portfolio_Return_Base100'] = (df_portfolio['Portfolio_Value'] / INITIAL_CAPITAL) * 100
    df_precos['IBOV_Return_Base100'] = (df_precos['IBOV'] / df_precos['IBOV'].iloc[0]) * 100

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.plot(df_portfolio.index, df_portfolio['Portfolio_Return_Base100'], 
           label='Estratégia Reversão à Média', color='royalblue', linewidth=2)
    ax.plot(df_precos.index, df_precos['IBOV_Return_Base100'], 
           label='IBOV (Benchmark)', color='darkorange', linewidth=2, linestyle='--')

    ax.set_title('Curva de Capital Comparativa (2010-2024)', fontsize=16, fontweight='bold')
    ax.set_xlabel('Ano', fontsize=12)
    ax.set_ylabel('Crescimento do Capital (Base 100)', fontsize=12)
    ax.legend(fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{int(x)}'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig('equity_curve_final.png', dpi=300)
    print("Gráfico 'equity_curve_final.png' salvo com sucesso!")

def main():
    """Função principal que executa o backtest completo"""
    print("=== INICIANDO BACKTEST DA ESTRATÉGIA DE REVERSÃO À MÉDIA ===")
    
    # Executa todas as etapas
    df_precos, tickers_acoes = carregar_dados()
    if df_precos is not None:
        df_sinais = gerar_sinais(df_precos, tickers_acoes)
        df_portfolio, INITIAL_CAPITAL = executar_backtest(df_precos, df_sinais, tickers_acoes)
        df_results = calcular_metricas(df_portfolio, df_precos, INITIAL_CAPITAL)
        plotar_resultados(df_portfolio, df_precos, INITIAL_CAPITAL)
        print("\n=== BACKTEST CONCLUÍDO ===")

if __name__ == '__main__':
    main()