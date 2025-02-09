from indicators import INDICATORS_MAP
from fetch import get_settings


def check():
    notes = {}
    for indicator_name, indicator_func in INDICATORS_MAP.items():
        # Pega as configurações da aba correspondente
        df = get_settings(indicator_name)

        if(df is None):
            print(f"Erro ao buscar configurações para {indicator_name}")
            continue

        # Chama a função do indicador com os dados obtidos
        indicator_note = indicator_func(df)

        # Adiciona as notas ao dicionário
        for symbol, symbol_notes in indicator_note.items():
            if symbol not in notes:
                notes[symbol] = []
            notes[symbol].append(symbol_notes)

    return notes

