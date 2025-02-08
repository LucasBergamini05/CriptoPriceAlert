import requests
import pandas as pd
import ta
import smtplib
import os
from email.mime.text import MIMEText

# Configurações do e-mail
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_TO = os.getenv("EMAIL_TO")

# Obtém os top 100 ativos da CoinGecko
def get_top_100_symbols():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1}
    response = requests.get(url, params=params)
    data = response.json()
    symbols = [coin["symbol"].upper() + "USDT" for coin in data]  # Adiciona 'USDT' para corresponder aos pares na Binance
    return symbols

# Obtém os últimos 20 candles de 4h para um ativo
def get_klines(symbol):
    url = f"https://api.binance.us/api/v3/klines"

    params = {"symbol": symbol, "interval": "4h", "limit": 20}

    response = requests.get(url, params=params)
    data = response.json()
    
    if "code" in data:  # Erro na API
        print(f"Erro ao buscar {symbol}: {data}")
        return None
    
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume", "close_time",
                                     "quote_volume", "trades", "taker_base", "taker_quote", "ignore"])
    df["close"] = df["close"].astype(float)
    return df

# Calcula Bandas de Bollinger e verifica se está abaixo da inferior
def check_bollinger_breach(symbol):
    df = get_klines(symbol)
    if df is None:
        return False

    # Calcula as Bandas de Bollinger (20 períodos, 3 desvios padrão)
    indicator_bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=3)
    df["bb_lower"] = indicator_bb.bollinger_lband()
    
    # Verifica se o preço atual está abaixo da banda inferior
    last_close = df["close"].iloc[-1]
    last_bb_lower = df["bb_lower"].iloc[-1]
    
    return last_close < last_bb_lower

# Envia e-mail com os ativos que romperam a banda inferior
def send_email(assets):
    if not assets:
        return
    
    subject = "⚠️ Alerta de Criptomoeda - Banda de Bollinger"
    body = f"As seguintes criptomoedas estão abaixo da banda de Bollinger de 3 desvios:\n\n" + "\n".join(assets)
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        print("📩 E-mail enviado com sucesso!")
    except Exception as e:
        print("Erro ao enviar e-mail:", e)

# 🚀 Fluxo Principal
def main():
    symbols = get_top_100_symbols()
    breached_assets = [symbol for symbol in symbols if check_bollinger_breach(symbol)]
    
    if breached_assets:
        print("⚠️ Ativos abaixo da banda inferior:", breached_assets)
        send_email(breached_assets)
    else:
        print("✅ Nenhum ativo rompeu a banda inferior.")

# Executa o script
if __name__ == "__main__":
    main()
