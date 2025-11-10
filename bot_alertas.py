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

# === MAPA BINANCE ===
MONEDAS = [
    "bitcoin", "ethereum", "bnb", "solana", "arbitrum", "optimism",
    "polygon", "render", "injective", "fet", "aave", "uniswap",
    "sand", "mana", "axie", "xrp", "tia", "sei"
]

PARES = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "bnb": "BNBUSDT",
    "solana": "SOLUSDT",
    "arbitrum": "ARBUSDT",
    "optimism": "OPUSDT",
    "polygon": "MATICUSDT",
    "render": "RNDRUSDT",
    "injective": "INJUSDT",
    "fet": "FETUSDT",
    "aave": "AAVEUSDT",
    "uniswap": "UNIUSDT",
    "sand": "SANDUSDT",
    "mana": "MANAUSDT",
    "axie": "AXSUSDT",
    "xrp": "XRPUSDT",
    "tia": "TIAUSDT",
    "sei": "SEIUSDT"
}

# === FUNCIONES ===
def obtener_precios(coin):
    """
    Obtiene los últimos 100 datos de 1 hora desde Binance.
    """
    try:
        symbol = PARES.get(coin.lower())
        if not symbol:
            raise ValueError(f"Símbolo no reconocido para {coin}")

        url = f"https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1h", "limit": 500}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if not isinstance(data, list) or len(data) == 0:
            raise ValueError(f"Sin datos para {coin}")

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "num_trades", "taker_base_vol",
            "taker_quote_vol", "ignore"
        ])

        df["time"] = pd.to_datetime(df["open_time"], unit="ms")
        df["price"] = df["close"].astype(float)
        return df[["time", "price"]]

    except Exception as e:
        print(f"⚠️ Error al obtener precios de {coin}: {e}")
        return pd.DataFrame(columns=["time", "price"])


def calcular_indicadores(df):
    """
    Calcula RSI (14) y MACD (12, 26, 9).
    """
    df["rsi"] = RSIIndicator(df["price"], window=14).rsi()
    macd = MACD(df["price"], window_slow=26, window_fast=12, window_sign=9)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    return df


def generar_senal(df):
    """
    Genera señal técnica si RSI y MACD coinciden.
    """
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


def guardar_alertas(alertas):
    """
    Guarda las alertas nuevas en un archivo JSON (máx. 100).
    """
    try:
        with open(RUTA_JSON, "r") as f:
            actuales = json.load(f)
    except:
        actuales = []

    if not isinstance(actuales, list):
        actuales = []

    actuales = alertas + actuales
    actuales = actuales[:100]

    with open(RUTA_JSON, "w") as f:
        json.dump(actuales, f, indent=4)

    print(f"✅ Guardadas {len(alertas)} alertas en {RUTA_JSON}")


def ejecutar():
    """
    Recorre las monedas, calcula RSI y MACD, genera alertas y las guarda.
    """
    alertas = []
    for coin in MONEDAS:
        df = obtener_precios(coin)
        if df.empty:
            continue

        df = calcular_indicadores(df)
        senal, rsi, macd, macd_signal, precio = generar_senal(df)
        print(f"{coin.upper():<10} | Precio: {precio:.2f} | RSI: {rsi:.2f} | MACD: {macd:.4f} | Señal: {senal or '-'}")

        if senal:
            alertas.append({
                "symbol": coin.upper(),
                "tipo": senal,
                "precio": round(float(precio), 2),
                "rsi": round(float(rsi), 2),
                "macd": "Alcista" if macd > macd_signal else "Bajista",
                "hora": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            })

    if alertas:
        guardar_alertas(alertas)
    else:
        print("⏳ Sin nuevas señales.")


# === EJECUCIÓN PRINCIPAL ===
if __name__ == "__main__":
    ejecutar()
