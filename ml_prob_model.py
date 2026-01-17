import yfinance as yf
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from issi_symbols import ISSI_BATCHES

# =====================================================
# Helper: RSI
# =====================================================
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# =====================================================
# Ambil list saham ISSI
# =====================================================
def get_all_symbols():
    symbols = []
    for batch in ISSI_BATCHES:
        symbols.extend(batch)
    return symbols


# =====================================================
# Generate fitur machine learning
# =====================================================
def make_features(df):
    df["return_1d"] = df["Close"].pct_change()
    df["return_3d"] = df["Close"].pct_change(3)

    df["rsi14"] = rsi(df["Close"], 14)

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()

    df["ma20_diff"] = (df["Close"] - df["ma20"]) / df["ma20"]
    df["ma60_diff"] = (df["Close"] - df["ma60"]) / df["ma60"]

    df["vol_std10"] = df["Close"].pct_change().rolling(10).std()

    df["vol_ma20"] = df["Volume"].rolling(20).mean()
    df["vol_ratio"] = df["Volume"] / df["vol_ma20"]

    df = df.dropna()
    return df


# =====================================================
# Generate label TP +10% (3 hari & 1 tahun)
# =====================================================
def make_labels(df):
    df["future_max_3d"] = df["High"].rolling(3).max().shift(-3)
    df["future_max_250d"] = df["High"].rolling(250).max().shift(-250)

    df["label_3d"] = (df["future_max_3d"] >= df["Close"] * 1.10).astype(int)
    df["label_1y"] = (df["future_max_250d"] >= df["Close"] * 1.10).astype(int)

    df = df.dropna()
    return df


# =====================================================
# Training model (jalankan sekali saja)
# =====================================================
def train_models():
    symbols = get_all_symbols()
    X_short = []
    y_short = []
    X_long = []
    y_long = []

    print(f"📥 Mengumpulkan data 3 tahun untuk {len(symbols)} saham...")

    for sym in symbols:
        df = yf.download(sym, period="3y", interval="1d", progress=False)
        if df.empty:
            continue

        df = make_features(df)
        df = make_labels(df)

        features = df[[
            "return_1d", "return_3d", "rsi14",
            "ma20_diff", "ma60_diff", "vol_std10", "vol_ratio"
        ]]

        X_short.extend(features.values.tolist())
        y_short.extend(df["label_3d"].values.tolist())

        X_long.extend(features.values.tolist())
        y_long.extend(df["label_1y"].values.tolist())

    print("📊 Training model short-term (3 hari)...")
    model_short = RandomForestClassifier(n_estimators=100, random_state=42)
    model_short.fit(X_short, y_short)
    pickle.dump(model_short, open("model_short.pkl", "wb"))

    print("📊 Training model long-term (1 tahun)...")
    model_long = RandomForestClassifier(n_estimators=100, random_state=42)
    model_long.fit(X_long, y_long)
    pickle.dump(model_long, open("model_long.pkl", "wb"))

    print("✅ Semua model telah selesai dilatih & disimpan!")


# =====================================================
# Fungsi prediksi yang dipakai screener.py
# =====================================================
def predict_probabilities(symbol):
    try:
        df = yf.download(symbol, period="3y", interval="1d", progress=False)
        if df.empty:
            return 0, 0

        df = make_features(df)
        last = df.iloc[-1]

        X = [[
            last["return_1d"],
            last["return_3d"],
            last["rsi14"],
            last["ma20_diff"],
            last["ma60_diff"],
            last["vol_std10"],
            last["vol_ratio"],
        ]]

        model_short = pickle.load(open("model_short.pkl", "rb"))
        model_long = pickle.load(open("model_long.pkl", "rb"))

        prob_3d = model_short.predict_proba(X)[0][1]
        prob_1y = model_long.predict_proba(X)[0][1]

        # convert to %
        return round(prob_3d * 100), round(prob_1y * 100)
    except:
        return 0, 0
