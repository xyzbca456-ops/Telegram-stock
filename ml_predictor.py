import joblib
import pandas as pd
import numpy as np
import yfinance as yf

# =======================================================
# === FUNGSI TEKNIKAL (SAMA DENGAN TRAINING) ============
# =======================================================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def prepare_features(df):
    df["return"] = df["Close"].pct_change()
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()
    df["rsi14"] = rsi(df["Close"], 14)
    df["vol_avg20"] = df["Volume"].rolling(20).mean()
    df = df.dropna()
    return df

# =======================================================
# === LOAD MODEL & PREDIKSI =============================
# =======================================================

def load_model(symbol):
    model_3hari = joblib.load(f"{symbol}_TP10_3hari.pkl")
    model_1tahun = joblib.load(f"{symbol}_TP10_1tahun.pkl")
    return model_3hari, model_1tahun


def predict_prob(symbol):
    """
    Mengembalikan:
    - Probabilitas TP 10% dalam 3 hari
    - Probabilitas TP 10% dalam 1 tahun
    """
    df = yf.download(symbol, period="6mo", interval="1d")

    if df is None or df.empty:
        return 0.0, 0.0

    df = prepare_features(df)
    latest = df.iloc[-1:]  # hanya 1 data terakhir

    features = ["return", "ma20", "ma60", "rsi14", "vol_avg20"]
    X = latest[features]

    try:
        model_3hari, model_1tahun = load_model(symbol)
    except:
        return 0.0, 0.0  # jika model belum ada

    prob_3hari = model_3hari.predict_proba(X)[0][1]
    prob_1tahun = model_1tahun.predict_proba(X)[0][1]

    return prob_3hari, prob_1tahun


# =======================================================
# === TEST LANGSUNG =====================================
# =======================================================

if __name__ == "__main__":
    s = "BBCA.JK"
    p3, p1 = predict_prob(s)
    print(f"{s} → 3 Hari: {p3:.2%}, 1 Tahun: {p1:.2%}")
