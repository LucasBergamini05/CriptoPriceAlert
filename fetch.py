import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# URL da API da Binance 
# (No GitHub, é binance.us, mas, localmente, é binance.com)
BINANCE_API_LINK = os.getenv("BINANCE_API_LINK")


# Obtém as configurações de uma aba da planilha de configurações
def get_settings(sheet):
    # URL da planilha com a Google Visualization API
    sheet_url = f"https://docs.google.com/spreadsheets/d/1rVBZyb8AzSZiI4RPl0NJ6w8fnN4ksxG0v44x62ct52c/gviz/tq?tqx=out:csv&sheet={sheet.replace(' ', '%20')}"

    # Lê os dados como DataFrame
    df = pd.read_csv(sheet_url)

    # Verifica se o indicador procurado é o mesmo da aba 
    if(df["Indicador"][0] != sheet):
        return None

    return df

# Obtém os últimos candles de um ativo
def get_klines(symbol, interval="4h", limit=20):
    url = f"{BINANCE_API_LINK}/api/v3/klines"

    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()
    
    # Erro na API
    if "code" in data:  
        print(f"Erro ao buscar {symbol}: {data}")
        return None
    
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_volume", "trades", "taker_base", "taker_quote", "ignore"])
    df["close"] = df["close"].astype(float)
    return df
