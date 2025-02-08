import requests
import pandas as pd
import ta
import os
from dotenv import load_dotenv

load_dotenv()

# URL da API da Binance 
# (No GitHub, é binance.us, mas, localmente, é binance.com)
BINANCE_API_LINK = os.getenv("BINANCE_API_LINK")

# Obtém os top 50 ativos da CoinGecko
def get_top_100_symbols():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
    response = requests.get(url, params=params)
    data = response.json()
    symbols = [coin["symbol"].upper() + "USDT" for coin in data]  # Adiciona 'USDT' para corresponder aos pares na Binance
    return symbols

# Obtém os últimos 20 candles de 4h para um ativo
def get_klines(symbol):
    url = f"{BINANCE_API_LINK}/api/v3/klines"

    params = {"symbol": symbol, "interval": "4h", "limit": 20}

    response = requests.get(url, params=params)
    data = response.json()
    
    if "code" in data:  # Erro na API
        print(f"Erro ao buscar {symbol}: {data}")
        return None
    
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_volume", "trades", "taker_base", "taker_quote", "ignore"])
    df["close"] = df["close"].astype(float)
    return df

# Calcula Bandas de Bollinger e verifica se está abaixo da inferior
def check_bollinger_breach(symbol):
    df = get_klines(symbol)
    if df is None:
        return False

    # Calcula as Bandas de Bollinger (20 períodos, 3 desvios padrão)
    indicator_bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=3)
    df["bb_lower"] = indicator_bb.bollinger_lband()
    df["bb_upper"] = indicator_bb.bollinger_hband()
    
    # Verifica se o preço atual está abaixo da banda inferior
    last_close = df["close"].iloc[-1]
    last_bb_lower = df["bb_lower"].iloc[-1]
    last_bb_upper = df["bb_upper"].iloc[-1]
    
    return last_close < last_bb_lower or last_close > last_bb_upper

def check():
    symbols = get_top_100_symbols()
    print(symbols)
    breached_assets = [symbol for symbol in symbols if check_bollinger_breach(symbol)]
    print(breached_assets)
    
    return breached_assets