from mail import send_email
from check import check
from last_alerts import handle_alerts

# Fluxo Principal
def main():
    print("🔍 Verificando alertas de preços...")
    assets_notes = handle_alerts(check())

    if assets_notes:
        send_email(assets_notes)

# Executa o script
if __name__ == "__main__":
    main()
