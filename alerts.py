import pandas as pd
from fetch import get_klines
from technical_analisys import check_bollinger_breach, calculate_sma, calculate_ema, compare_values
from commons import prepare_dataframe, get_message_map

# Realiza a verificação da BB nos ativos com suas respectivas configurações
def handle_bollinger_alert(df: pd.DataFrame):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int),
        "window_dev": ("Desvio", 3, float)
    })

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
            symbols_notes[symbol] = f"Preço abaixo da Banda Inferior de Bollinger {settings["interval"]} ↘️"
            continue

        if result == 1:
            symbols_notes[symbol] = f"Preço acima da Banda Superior de Bollinger {settings["interval"]} ↗️"
      
    return symbols_notes


def handle_volume_alert(df: pd.DataFrame):
    # Formata o DataFrame
    prepare_dataframe(df, {
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int)
    })

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
            symbols_notes[symbol] = f"Volume acima da média ({settings["interval"]}) ↗️"

    return symbols_notes


def handle_current_price_alert(df: pd.DataFrame):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "interval": ("Tempo Gráfico", "4h", str),
        "price": ("Valor", None, float),
        "type": ("Tipo", ">", str)
    })

    # Cria um dicionário com as configurações
    price_settings = df.set_index("Ativo")[["interval", "price", "type"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in price_settings.items():
        price = settings["price"]
        type = settings["type"]
        interval = settings["interval"]

        df = get_klines(symbol, interval=interval, limit=1)
        if df is None:
            continue

        last_price = float(df["close"].iloc[-1])

        if compare_values(last_price, price, type):
            symbols_notes[symbol] = get_message_map(price, type, interval)

    return symbols_notes


def handle_moving_average_alert(df: pd.DataFrame):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int),
        "type": ("Tipo de Média", "SMA", str),
        "comparison": ("Comparação", ">", str)
    })

    # Cria um dicionário com as configurações
    ma_settings = df.set_index("Ativo")[["interval", "window", "type", "comparison"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in ma_settings.items():
        type = settings["type"]
        comparison = settings["comparison"]
        window = settings["window"]
        interval = settings["interval"]

        df = get_klines(symbol, interval=interval, limit=window)
        if df is None:
            continue

        if type == "SMA":
            result = calculate_sma(df["close"], window=window)
        else:
            result = calculate_ema(df["close"], window=window)

        last_price = float(df["close"].iloc[-1])
        last_ma = float(result.iloc[-1])

        ma_text = f"{type} de {window} períodos"

        if compare_values(last_price, last_ma, comparison):
            symbols_notes[symbol] = get_message_map(ma_text, comparison, interval)
    return symbols_notes
        

ALERTS_MAP = {
    "Bollinger Bands": handle_bollinger_alert,
    "Volume": handle_volume_alert,
    "Valor Atual": handle_current_price_alert,
    "Media Movel": handle_moving_average_alert
}
