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
        interval, window, window_dev = (settings.get(k) for k in ("interval", "window", "window_dev"))

        klines_df = get_klines(symbol, interval=interval, limit=window)
        if klines_df is None:
            continue
        
        result = check_bollinger_breach(klines_df, window=window, window_dev=window_dev)

        if result == -1:
            symbols_notes[symbol] = f"Preço abaixo da Banda Inferior de Bollinger {interval} ↘️"
            continue

        if result == 1:
            symbols_notes[symbol] = f"Preço acima da Banda Superior de Bollinger ({interval}) ↗️"
      
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
        interval, window = (settings.get(k) for k in ("interval", "window"))

        klines_df = get_klines(symbol, interval=interval, limit=window)
        if klines_df is None:
            continue
        
        result = calculate_sma(klines_df["volume"], window=window)

        last_open = float(klines_df["open"].iloc[-1])
        last_close = float(klines_df["close"].iloc[-1])

        last_volume = float(klines_df["volume"].iloc[-1])
        last_volume_median = float(result.iloc[-1])

        candle_color = "verde" if last_close > last_open else "vermelho"

        if last_volume > last_volume_median:
            symbols_notes[symbol] = f"Volume acima da média em candle {candle_color} ({interval}) ↗️"

    return symbols_notes


def handle_current_price_alert(df: pd.DataFrame):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "interval": ("Tempo Gráfico", "4h", str),
        "price": ("Valor", None, float),
        "comparison": ("Comparação", ">", str)
    })

    # Cria um dicionário com as configurações
    price_settings = df.set_index("Ativo")[["interval", "price", "comparison"]].to_dict(orient="index")

    # Verifica os ativos
    symbols_notes = {}
    for symbol, settings in price_settings.items():
        price, comparison, interval = (settings.get(k) for k in ("price", "comparison", "interval"))

        klines_df = get_klines(symbol, interval=interval, limit=1)
        if klines_df is None:
            continue

        last_price = float(klines_df["close"].iloc[-1])

        if compare_values(last_price, price, comparison):
            symbols_notes[symbol] = get_message_map(price, comparison, interval)

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
        type, comparison, window, interval = (settings.get(k) for k in ("type", "comparison", "window", "interval"))

        klines_df = get_klines(symbol, interval=interval, limit=window)
        if klines_df is None:
            continue

        if type == "SMA":
            result = calculate_sma(klines_df["close"], window=window)
        else:
            result = calculate_ema(klines_df["close"], window=window)

        last_price = float(klines_df["close"].iloc[-1])
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
