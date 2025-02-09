import pandas as pd
import ta

# Verifica se o preço de fechamento está fora das Bandas de Bollinger
def check_bollinger_breach(df: pd.DataFrame, window=20, window_dev=3):
    # Calcula as Bandas de Bollinger
    indicator_bb = ta.volatility.BollingerBands(close=df["close"], window=window, window_dev=window_dev)
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

# Calcula a Média Móvel Simples de uma série de valores
def calculate_sma(series: pd.Series, window=20):
    return series.rolling(window=window).mean()

def compare_values(first_value, second_value, type):
    def is_price_above(price, last_price):
        return last_price > price

    def is_price_below(price, last_price):
        return last_price < price

    def is_price_equal_or_above(price, last_price):
        return last_price >= price

    def is_price_equal_or_below(price, last_price):
        return last_price <= price

    type_map = {
        ">": is_price_above,
        "<": is_price_below,
        ">=": is_price_equal_or_above,
        "<=": is_price_equal_or_below
    }

    compare_function = type_map.get(type)

    if compare_function is not None:
        return compare_function(first_value, second_value)
    
    print(f"Tipo de comparação inválido: {type}")
