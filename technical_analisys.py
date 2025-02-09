
import ta

# Verifica se o preço de fechamento está fora das Bandas de Bollinger
def check_bollinger_breach(df, window=20, window_dev=3):
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
