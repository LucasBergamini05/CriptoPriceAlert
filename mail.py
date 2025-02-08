import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do e-mail
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_TO = os.getenv("EMAIL_TO")

# Envia e-mail com os ativos que romperam a banda inferior
def send_email(assets):
    # if not assets:
    #     return
    
    subject = "⚠️ Alerta de Criptomoeda - Banda de Bollinger"
    body = f"As seguintes criptomoedas estão fora das bandas de Bollinger de 3 desvios:\n\n" + "\n".join(assets)
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
    server.quit()
    print("📩 E-mail enviado com sucesso!")
