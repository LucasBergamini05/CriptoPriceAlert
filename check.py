from alerts import ALERTS_MAP
from fetch import get_settings

# Realiza a verificação dos alertas
def check():
    notes = {}
    for alert_name, alert_func in ALERTS_MAP.items():
        # Pega as configurações da aba correspondente
        df = get_settings(alert_name)

        if(df is None):
            print(f"Erro ao buscar configurações para {alert_name}")
            continue

        # Chama a função do alerta com os dados obtidos
        alert_note = alert_func(df)

        # Adiciona as notas ao dicionário
        for symbol, symbol_notes in alert_note.items():
            if symbol not in notes:
                notes[symbol] = []
            notes[symbol].append(symbol_notes)

    return notes
