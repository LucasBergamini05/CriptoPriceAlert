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
def send_email(assets_notes):
    # if not assets:
    #     return
    
    subject = "⚠️ Alerta de Criptomoeda"

    body = ""

    for pair, notes in assets_notes.items():
        body += f"{pair}:\n"
        for note in notes:
            body += f" - {note}\n"
        body += "\n"
    
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
