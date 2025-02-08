from mail import send_email
from check import check

# 🚀 Fluxo Principal
def main():
    breached_assets = check()
    
    if breached_assets:
        print("⚠️ Ativos fora das bandas Bollinger:", breached_assets)
        send_email(breached_assets)
    else:
        print("✅ Nenhum ativo fora das bandas de Bollinger.")

# Executa o script
if __name__ == "__main__":
    main()
