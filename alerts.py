import pandas as pd
from fetch import get_klines
from technical_analisys import check_bollinger_breach, calculate_sma, calculate_ema, compare_values

# Realiza a verificação da BB nos ativos com suas respectivas configurações
def handle_bollinger_alert(df: pd.DataFrame):
    # Configurações padrão
    default_settings = {"interval": "4h", "window": 20, "window_dev": 3}

    # Converte os valores para o formato correto e preenche com as configurações padrão
    df["interval"] = df["Tempo Gráfico"].apply(lambda x: default_settings["interval"] if pd.isna(x) else x)
    df["window"] = pd.to_numeric(df["Intervalo"], errors="coerce").apply(lambda x: default_settings["window"] if pd.isna(x) else int(x))
    df["window_dev"] = pd.to_numeric(df["Desvio"], errors="coerce").apply(lambda x: default_settings["window_dev"] if pd.isna(x) else float(x))

    # Cria um dicionário com as configurações
    bollinger_settings = df.set_index("Ativo")[["interval", "window", "window_dev"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in bollinger_settings.items():
        df = get_klines(symbol, interval=settings["interval"], limit=settings["window"])
        if df is None:
            continue
        
        result = check_bollinger_breach(df, window=settings["window"], window_dev=settings["window_dev"])

        if result == -1:
            symbols_notes[symbol] = "Preço abaixo da Banda Inferior de Bollinger ↘️"
            continue

        if result == 1:
            symbols_notes[symbol] = "Preço acima da Banda Superior de Bollinger ↗️"
      
    return symbols_notes

def handle_volume_alert(df: pd.DataFrame):
    # Configurações padrão
    default_settings = {"interval": "4h", "window": 20}

    # Converte os valores para o formato correto e preenche com as configurações padrão
    df["interval"] = df["Tempo Gráfico"].apply(lambda x: default_settings["interval"] if pd.isna(x) else x)
    df["window"] = pd.to_numeric(df["Intervalo"], errors="coerce").apply(lambda x: default_settings["window"] if pd.isna(x) else int(x))

    # Cria um dicionário com as configurações
    volume_settings = df.set_index("Ativo")[["interval", "window"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in volume_settings.items():
        df = get_klines(symbol, interval=settings["interval"], limit=settings["window"])
        if df is None:
            continue
        
        result = calculate_sma(df["volume"], window=settings["window"])

        last_volume = float(df["volume"].iloc[-1])
        last_volume_median = float(result.iloc[-1])

        if last_volume > last_volume_median:
            symbols_notes[symbol] = "Volume acima da média ↗️"

    return symbols_notes

def handle_current_price_alert(df: pd.DataFrame):
    # Configurações padrão
    default_settings = {"interval": "4h"}

    # Converte os valores para o formato correto e preenche com as configurações padrão
    df["interval"] = df["Tempo Gráfico"].apply(lambda x: default_settings["interval"] if pd.isna(x) else x)
    df["price"] = df["Valor"]
    df["type"] = df["Tipo"]

    # Cria um dicionário com as configurações
    price_settings = df.set_index("Ativo")[["interval", "price", "type"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in price_settings.items():
        df = get_klines(symbol, interval=settings["interval"], limit=1)
        if df is None:
            continue

        last_price = float(df["close"].iloc[-1])
        price = settings["price"]
        type = settings["type"]

        message_map = {
            ">": f"Preço acima de {price} ↗️",
            "<": f"Preço abaixo de {price} ↘️",
            ">=": f"Preço igual ou acima de {price} ↗️",
            "<=": f"Preço igual ou abaixo de {price} ↘️"
        }

        if type in message_map and compare_values(last_price, price, type):
            symbols_notes[symbol] = message_map.get(type)

    return symbols_notes

def handle_ma_alert(df: pd.DataFrame):
    # Configurações padrão
    default_settings = {"interval": "4h", "window": 20, "type": "SMA"}

    # Converte os valores para o formato correto e preenche com as configurações padrão
    df["interval"] = df["Tempo Gráfico"].apply(lambda x: default_settings["interval"] if pd.isna(x) else x)
    df["window"] = pd.to_numeric(df["Intervalo"], errors="coerce").apply(lambda x: default_settings["window"] if pd.isna(x) else int(x))
    df["type"] = df["Tipo de Média"].apply(lambda x: default_settings["type"] if pd.isna(x) else x)
    df["comparison"] = df["Comparação"]

    # Cria um dicionário com as configurações
    ma_settings = df.set_index("Ativo")[["interval", "window", "type", "comparison"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in ma_settings.items():
        type = settings["type"]
        comparison = settings["comparison"]
        window = settings["window"]

        df = get_klines(symbol, interval=settings["interval"], limit=window)
        if df is None:
            continue
        

        if type == "SMA":
            result = calculate_sma(df["close"], window=window)
        else:
            result = calculate_ema(df["close"], window=window)


        last_price = float(df["close"].iloc[-1])
        last_ma = float(result.iloc[-1])

        ma_text = f"{type} de {window} períodos ({settings['interval']})"

        message_map = {
            ">": f"Preço acima da {ma_text} ↗️",
            "<": f"Preço abaixo da {ma_text} ↘️",
            ">=": f"Preço igual ou acima da {ma_text} ↗️",
            "<=": f"Preço igual ou abaixo da {ma_text} ↘️",
        }

        if comparison in message_map and compare_values(last_price, last_ma, comparison):
            symbols_notes[symbol] = message_map.get(comparison)

    return symbols_notes
        

ALERTS_MAP = {
    "Bollinger Bands": handle_bollinger_alert,
    "Volume": handle_volume_alert,
    "Valor Atual": handle_current_price_alert,
    "Media Movel": handle_ma_alert
}
