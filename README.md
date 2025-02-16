# Crypto Price Alerts

Este projeto realiza verificações em criptoativos, definidos em uma planilha, usando indicadores técnicos e gera alertas com base em diferentes critérios.


## Funcionalidades

- Configurações: Consulta em uma planilha as configurações dos alertas;

- Valor Atual: Compara o preço atual com um valor definido;

- Bollinger Bands: Identifica quando o preço cruza as bandas superior e inferior;

- Volume: Verifica se o volume atual está acima da média móvel;

- Média Móvel (SMA/EMA): Compara o preço atual com uma média móvel;

- Notificação periódica: Envia um E-mail contendo as notas dos alertas periodicamente.

## Estrutura do Código

```plaintext
.github/
└── workflows             
    └── workflows          # coin_alert.yml
app/
├── alerts.py              # Arquivo com as funções de cada alertas
├── check.py               # Função que realiza as verificações
├── commons.py             # Funções comuns
├── fetch.py               # Funções para consultar a planilha de configurações e os ativos na Binance
├── mail.py                # Função que dispara o e-mail
├── main.py                # Arquivo principal
└── technical_analisys.py  # Funções para análise técnica
```
