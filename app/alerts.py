import pandas as pd
from fetch import get_klines
from technical_analisys import check_bollinger_breach, calculate_sma, calculate_ema, compare_values
from commons import prepare_dataframe, get_message_map, add_symbol_note

# Verifica se o preço atual está fora das Bandas de Bollinger
def handle_bollinger_alert(df: pd.DataFrame, symbols_notes):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "symbol": ("Ativo", None, str),
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int),
        "window_dev": ("Desvio", 3, float),
    })

    # Verifica os ativos
    for row in df.itertuples():
        symbol, interval, window, window_dev = row.symbol, row.interval, row.window, row.window_dev

        klines_df = get_klines(symbol, interval=interval, limit=window)
        if klines_df is None:
            continue

        result = check_bollinger_breach(klines_df, window=window, window_dev=window_dev)

        if result == -1:
            add_symbol_note(symbols_notes, symbol, f"Preço abaixo da Banda Inferior de Bollinger ({interval}) ↘️")
            continue

        if result == 1:
            add_symbol_note(symbols_notes, symbol, f"Preço acima da Banda Superior de Bollinger ({interval}) ↗️")

    return symbols_notes


#  Comparação do volume atual com sua média móvel
def handle_volume_alert(df: pd.DataFrame, symbols_notes):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "symbol": ("Ativo", None, str),
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int),
        "candle_type": ("Tipo de Candle", "Ascendente", str),
    })

    # Verifica os ativos
    for row in df.itertuples():
        symbol, interval, window, candle_type = row.symbol, row.interval, row.window, row.candle_type

        klines_df = get_klines(symbol, interval=interval, limit=window)
        if klines_df is None:
            continue

        result = calculate_sma(klines_df["volume"], window=window)

        last_open = float(klines_df["open"].iloc[-1])
        last_close = float(klines_df["close"].iloc[-1])

        last_volume = float(klines_df["volume"].iloc[-1])
        last_volume_median = float(result.iloc[-1])

        current_candle_type = "Ascendente" if last_close > last_open else "Descendente"

        valid_volume = last_volume > last_volume_median

        valid_candle = candle_type == "Indiferente" or candle_type == current_candle_type

        if valid_volume and valid_candle:
            add_symbol_note(symbols_notes, symbol, f"Volume acima da média em candle {current_candle_type} ({interval}) ↗️")

    return symbols_notes


# Compara o preço atual com um valor
def handle_current_price_alert(df: pd.DataFrame, symbols_notes):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "symbol": ("Ativo", None, str),
        "price": ("Valor", None, float),
        "comparison": ("Comparação", ">", str),
    })

    # Verifica os ativos
    for row in df.itertuples():
        symbol, price, comparison =  row.symbol, row.price, row.comparison

        klines_df = get_klines(symbol, interval="1h", limit=1)
        if klines_df is None:
            continue

        last_price = float(klines_df["close"].iloc[-1])

        if compare_values(last_price, price, comparison):
            add_symbol_note(symbols_notes, symbol, get_message_map(price, comparison, "1h"))

    return symbols_notes


# Compara o preço atual com uma média móvel
def handle_moving_average_alert(df: pd.DataFrame, symbols_notes):
    # Formata o DataFrame
    df = prepare_dataframe(df, {
        "symbol": ("Ativo", None, str),
        "interval": ("Tempo Gráfico", "4h", str),
        "window": ("Intervalo", 20, int),
        "type": ("Tipo de Média", "SMA", str),
        "comparison": ("Comparação", ">", str),
    })

    # Verifica os ativos
    for row in df.itertuples():
        symbol, interval, window, type, comparison = row.symbol, row.interval, row.window, row.type, row.comparison

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
            add_symbol_note(symbols_notes, symbol, get_message_map(ma_text, comparison, interval))

    return symbols_notes


ALERTS_MAP = {
    "Bollinger Bands": handle_bollinger_alert,
    "Volume": handle_volume_alert,
    "Valor Atual": handle_current_price_alert,
    "Media Movel": handle_moving_average_alert
}
