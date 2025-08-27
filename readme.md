# Estratégia de Reversão à Média com Z-Score

Este projeto implementa uma estratégia quantitativa de reversão à média baseada em Z-scores para o mercado brasileiro, utilizando dados do Ibovespa e ações da B3.

## Descrição da Estratégia

A estratégia se baseia no conceito de reversão à média, onde:
- Compras são realizadas quando o Z-score < -2.0 (ativo subvalorizado)
- Vendas são realizadas quando o Z-score > 2.0 (ativo sobrevalorizado)
- Z-score é calculado usando janela móvel de 50 períodos

## Estrutura do Projeto

```
poliQuantCase/
│
├── grafico_retorno_estrategia_v1.py   # Código principal da estratégia
├── gerar_grafico_compras.py           # Análise dos sinais de compra
├── gerar_grafico_gaussiano_vendas.py  # Análise dos sinais de venda
├── ibov_2010_2024.csv                 # Dados históricos do Ibovespa
├── precos_b3_202010-2024.csv         # Dados históricos das ações
│
├── Outputs/
│   ├── equity_curve_final.png         # Curva de capital da estratégia
│   ├── distribuicao_zscores_compras.png
│   ├── distribuicao_zscores_vendas.png
│   ├── metricas_performance.csv
│   ├── resultados_backtest.csv
│   └── trade_signals.csv
```

## Requisitos

- Python 3.x
- Bibliotecas necessárias:
  ```bash
  pip install pandas numpy matplotlib seaborn scipy
  ```

## Como Usar

1. Prepare os dados:
   - Coloque os arquivos `ibov_2010_2024.csv` e `precos_b3_202010-2024.csv` na pasta do projeto

2. Execute o backtest principal:
   ```bash
   python grafico_retorno_estrategia_v1.py
   ```

3. Gere análises dos sinais de compra:
   ```bash
   python gerar_grafico_compras.py
   ```

4. Gere análises dos sinais de venda:
   ```bash
   python gerar_grafico_gaussiano_vendas.py
   ```

## Métricas de Performance

| Métrica | Estratégia | IBOV |
|---------|------------|------|
| Rentabilidade Total | 276.58% | 71.72% |
| Retorno Anualizado | 9.39% | 3.73% |
| Volatilidade Anualizada | 15.78% | 23.50% |
| Índice de Sharpe | 0.59 | 0.16 |
| Drawdown Máximo | -39.59% | -48.63% |

## Arquivos de Saída

- `equity_curve_final.png`: Gráfico comparativo da estratégia vs. IBOV
- `distribuicao_zscores_compras.png`: Distribuição dos Z-scores nas compras
- `distribuicao_zscores_vendas.png`: Distribuição dos Z-scores nas vendas
- `metricas_performance.csv`: Métricas detalhadas de performance
- `resultados_backtest.csv`: Resultados completos do backtest
- `trade_signals.csv`: Detalhes de todas as operações

## Parâmetros da Estratégia

- Capital Inicial: R$ 1.000.000,00
- Tamanho da Posição: R$ 50.000,00 por operação
- Janela do Z-score: 50 períodos
- Threshold de Compra: -2.0
- Threshold de Venda: +2.0

## Considerações

- A estratégia assume liquidez suficiente para todas as operações
- Custos de transação não são considerados
- Assume execução no preço de fechamento
- Rebalanceamento diário das posições

