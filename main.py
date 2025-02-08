from mail import send_email
from check import check

# 🚀 Fluxo Principal
def main():
    assets_notes = check()
    
    if assets_notes:
        print("⚠️ Alerta de preços:\n", assets_notes)
        send_email(assets_notes)
    else:
        print("✅ Nenhum alerta de preço.")

# Executa o script
if __name__ == "__main__":
    main()
