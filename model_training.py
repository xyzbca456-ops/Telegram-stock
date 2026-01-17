import yfinance as yf
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ============================================================
# === FUNGSI TEKNIKAL ===
# ============================================================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def make_features(df):
    df["return"] = df["Close"].pct_change()
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()
    df["rsi14"] = rsi(df["Close"], 14)
    df["vol_avg20"] = df["Volume"].rolling(20).mean()

    df = df.dropna()
    return df

# ============================================================
# === LABEL TARGET ===
# ============================================================

def label_tp10_3hari(df):
    df["target_3hari"] = (
        df["Close"].shift(-3) >= df["Close"] * 1.10
    ).astype(int)
    return df

def label_tp10_1tahun(df):
    df["target_1tahun"] = (
        df["Close"].shift(-252) >= df["Close"] * 1.10
    ).astype(int)
    return df

# ============================================================
# === TRAINING MODEL ===
# ============================================================

def train_model(df, target_col, model_name):
    features = ["return", "ma20", "ma60", "rsi14", "vol_avg20"]
    df = df.dropna()

    X = df[features]
    y = df[target_col]

    # Train-test split (tidak terlalu penting, tapi membantu stabilitas)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42
    )
    model.fit(X_train, y_train)

    joblib.dump(model, model_name)
    print(f"Model saved: {model_name}")


# ============================================================
# === MAIN TRAINING PROGRAM ===
# ============================================================

def train_all(symbol):
    print(f"Downloading 3 years data for {symbol} ...")
    df = yf.download(symbol, period="3y", interval="1d")

    df = make_features(df)
    df = label_tp10_3hari(df)
    df = label_tp10_1tahun(df)

    train_model(df, "target_3hari", f"{symbol}_TP10_3hari.pkl")
    train_model(df, "target_1tahun", f"{symbol}_TP10_1tahun.pkl")

    print("Training complete.")


# ============================================================
# === RUN (untuk seluruh daftar saham Indonesia di isii_symbols.py) ===
# ============================================================

if __name__ == "__main__":
    from issi_symbols import ISSI_SYMBOLS

    for symbol in ISSI_SYMBOLS:
        try:
            train_all(symbol)
        except Exception as e:
            print(f"Error training {symbol}: {e}")
