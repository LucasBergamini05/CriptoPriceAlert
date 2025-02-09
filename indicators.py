import pandas as pd
from fetch import get_klines
from technical_analisys import check_bollinger_breach

# Realiza a verificação da BB nos ativos com suas respectivas configurações
def handle_bollinger_indicator(df):
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
        
        bollinger_note = check_bollinger_breach(df, window=settings["window"], window_dev=settings["window_dev"])

        if bollinger_note == -1:
            symbols_notes[symbol] = "Preço abaixo da Banda Inferior de Bollinger ↘️"
            continue

        if bollinger_note == 1:
            symbols_notes[symbol] = "Preço acima da Banda Superior de Bollinger ↗️"
      
    return symbols_notes


INDICATORS_MAP = {
    "Bollinger Bands": handle_bollinger_indicator
}
