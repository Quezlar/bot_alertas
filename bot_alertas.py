"""
Bot automático RSI + MACD (4 criptos)
Versión final: consulta CoinGecko cada 10 min y envía alertas a tu web
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
URL_ALERTAS = "https://limpiezasroquez.com/api/index.php"
TOKEN = "MI_TOKEN_SECRETO_123"  # el mismo del PHP
MONEDAS = ["bitcoin", "ethereum", "zcash", "sui"]
VS_CURRENCY = "usd"
INTERVALO_MINUTOS = 10  # tiempo entre ciclos

# === FUNCIONES ===
def obtener_precios(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency={VS_CURRENCY}&days=1&interval=hourly"
    r = requests.get(url, timeout=10)
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
    if rsi < 30 and macd > macd_signal:
        senal = "COMPRA"
    elif rsi > 70 and macd < macd_signal:
        senal = "VENTA"
    return senal, rsi, macd, macd_signal, precio

def enviar_alertas(alertas):
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    try:
        r = requests.post(URL_ALERTAS, headers=headers, data=json.dumps(alertas), timeout=10)
        print(f"✅ Enviadas {len(alertas)} alertas:", r.text)
    except Exception as e:
        print("⚠️ Error al enviar:", e)

# === LOOP PRINCIPAL ===
def ejecutar():
    while True:
        alertas = []
        for coin in MONEDAS:
            try:
                df = obtener_precios(coin)
                df = calcular_indicadores(df)
                senal, rsi, macd, macd_signal, precio = generar_senal(df)
                if senal:
                    alertas.append({
                        "symbol": coin.upper(),
                        "tipo": senal,
                        "precio": round(float(precio), 2),
                        "rsi": round(float(rsi), 2),
                        "macd": "Alcista" if macd > macd_signal else "Bajista",
                        "hora": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    })
            except Exception as e:
                print(f"Error en {coin}:", e)

        if alertas:
            enviar_alertas(alertas)
        else:
            print("⏳ Sin nuevas señales.")
        print(f"Esperando {INTERVALO_MINUTOS} min...\n")
        time.sleep(INTERVALO_MINUTOS * 60)


# === Servidor "falso" para Render (mantiene el bot activo) ===
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def alive():
    return "🤖 Bot RSI+MACD funcionando correctamente!"

def mantener_vivo():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    hilo = Thread(target=mantener_vivo)
    hilo.start()
    ejecutar()
