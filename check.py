import requests
import pandas as pd
import ta
import os
from dotenv import load_dotenv

load_dotenv()

# Número de ativos a serem verificados
NUM_ASSETS = int(os.getenv("NUM_ASSETS"))

# URL da API da Binance 
# (No GitHub, é binance.us, mas, localmente, é binance.com)
BINANCE_API_LINK = os.getenv("BINANCE_API_LINK")

# Obtém os ativos da CoinGecko
def get_top_symbols():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": NUM_ASSETS, "page": 1}
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

# Verifica se o preço de fechamento está fora das Bandas de Bollinger
def check_bollinger_breach(df):
    # Calcula as Bandas de Bollinger (20 períodos, 3 desvios padrão)
    indicator_bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=3)
    df["bb_lower"] = indicator_bb.bollinger_lband()
    df["bb_upper"] = indicator_bb.bollinger_hband()
    
    # Compara o preço de fechamento com as bandas
    last_close = df["close"].iloc[-1]
    last_bb_lower = df["bb_lower"].iloc[-1]
    last_bb_upper = df["bb_upper"].iloc[-1]
    
    if(last_close < last_bb_lower):
        return -1
    
    if(last_close > last_bb_upper):
        return 1
    
    return 0


def check_symbol(symbol):
    notes = []

    df = get_klines(symbol)
    if df is None:
        return notes
    
    bollinger_note = check_bollinger_breach(df)

    if bollinger_note == -1:
        notes.append("Preço abaixo da Banda Inferior de Bollinger ↘️")

    elif bollinger_note == 1:
        notes.append("Preço acima da Banda Superior de Bollinger ↗️")
    

    return notes

def check():
    symbols = get_top_symbols()
    symbols_notes = {}

    for symbol in symbols:
        notes = check_symbol(symbol)
        if len(notes):
            symbols_notes[symbol] = notes
    
    return symbols_notes