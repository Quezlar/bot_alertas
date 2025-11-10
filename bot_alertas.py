"""
Bot de alertas RSI + MACD
Analiza BTC, ETH, ZEC y SUI desde CoinGecko
y envía señales a tu web (limpiezasroquez.com)
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD

# === CONFIGURACIÓN ===
URL_API = "https://api.coingecko.com/api/v3/coins/markets"
URL_ALERTAS = "https://limpiezasroquez.com/api/alertas.json"   # destino en tu web
MONEDAS = ["bitcoin", "ethereum", "zcash", "sui"]
VS_CURRENCY = "usd"

# === FUNCIONES ===
def obtener_precios(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency={VS_CURRENCY}&days=1&interval=hourly"
    r = requests.get(url)
    datos = r.json()["prices"]
    df = pd.DataFrame(datos, columns=["time", "price"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

def calcular_indicadores(df):
    df["rsi"] = RSIIndicator(df["price"], window=14).rsi()
    macd = MACD(df["price"], window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    return df

def generar_senal(df):
    rsi = df["rsi"].iloc[-1]
    macd = df["macd"].iloc[-1]
    macd_signal = df["macd_signal"].iloc[-1]
    precio = df["price"].iloc[-1]
    senal = None

    # Reglas básicas
    if rsi < 30 and macd > macd_signal:
        senal = "BUY"
    elif rsi > 70 and macd < macd_signal:
        senal = "SELL"
    return senal, rsi, macd, macd_signal, precio

def enviar_alerta(alertas):
    try:
        # Cargar alertas previas
        try:
            actuales = requests.get(URL_ALERTAS).json()
        except:
            actuales = []
        actuales.extend(alertas)
        # Subir al servidor
        headers = {"Content-Type": "application/json"}
        requests.post(URL_ALERTAS, data=json.dumps(actuales), headers=headers, timeout=10)
        print("✅ Alertas enviadas con éxito")
    except Exception as e:
        print("⚠️ Error al enviar alertas:", e)

# === LOOP PRINCIPAL ===
def ejecutar():
    alertas = []
    for coin in MONEDAS:
        try:
            df = obtener_precios(coin)
            df = calcular_indicadores(df)
            senal, rsi, macd, macd_signal, precio = generar_senal(df)
            if senal:
                alertas.append({
                    "symbol": coin.upper(),
                    "signal": senal,
                    "rsi": round(float(rsi),2),
                    "macd": "Alcista" if macd > macd_signal else "Bajista",
                    "price": round(float(precio),2),
                    "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"Error en {coin}:", e)

    if alertas:
        enviar_alerta(alertas)
    else:
        print("⏳ Sin nuevas alertas.")

if __name__ == "__main__":
    while True:
        ejecutar()
        time.sleep(600)  # Espera 10 minutos
