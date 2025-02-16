import pandas as pd

# Função para preparar o DataFrame
def prepare_dataframe(df, column_map):
    # Ajusta os nomes das colunas, preenche valores NaN e converte colunas para os tipos corretos.
    for col, (sheet_col,default, dtype) in column_map.items():
        df[col] = pd.to_numeric(df[sheet_col], errors="coerce") if dtype in [int, float] else df[sheet_col]
        df[col] = df[col].apply(lambda x: default if pd.isna(x) else dtype(x))
    return df


# Função para gerar mensagem de alerta
def get_message_map(metric, comparison, interval):
    return {
        ">": f"Preço acima de {metric} ({interval}) ↗️",
        "<": f"Preço abaixo de {metric} ({interval}) ↘️",
        ">=": f"Preço igual ou acima de {metric} ({interval}) ↗️",
        "<=": f"Preço igual ou abaixo de {metric} ({interval}) ↘️",
    }.get(comparison)


# Função para adicionar nota ao símbolo
def add_symbol_note(symbols_notes, symbol, message):
    if symbol not in symbols_notes:
        symbols_notes[symbol] = []
    symbols_notes[symbol].append(message)
