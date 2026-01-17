import yfinance as yf
import pandas as pd

# =====================================================
# RSI Function
# =====================================================
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# =====================================================
# Fibonacci Levels (untuk /scan)
# =====================================================
def get_fib_levels(df):
    high = float(df['High'].max())
    low = float(df['Low'].min())

    fib_786 = round(high - (high - low) * 0.786, 2)  
    fib_618 = round(high - (high - low) * 0.618, 2)  
    fib_50 = round(high - (high - low) * 0.50, 2)  
    tp_21 = round(high + (high - low) * 0.21, 2)  

    return {  
        "fib_786": fib_786,  
        "fib_618": fib_618,  
        "fib_50": fib_50,  
        "tp_21": tp_21  
    }

# =====================================================
# Ambil info saham tunggal
# =====================================================
def get_stock_info(symbol, period="3mo", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        if df.empty:
            return None

        close = df["Close"]  
        last_close = float(close.iloc[-1])  
        ma60 = float(close.rolling(60).mean().iloc[-1])  
        rsi_val = float(rsi(close).iloc[-1])  

        ma_status = "Above MA60" if last_close > ma60 else "Below MA60"  

        vol_last = float(df['Volume'].iloc[-1])  
        vol_ma20 = float(df['Volume'].rolling(20).mean().iloc[-1])  

        vol_status = "Normal ⚪"  
        if vol_last > 1.5 * vol_ma20:  
            vol_status = "High 🔵"  
        elif vol_last < 0.5 * vol_ma20:  
            vol_status = "Low 🔴"  

        value_last = round(last_close * vol_last)  
        value_ma20 = float((df['Close'] * df['Volume']).rolling(20).mean().iloc[-1])  

        value_status = "Normal ⚪"  
        if value_last > 1.5 * value_ma20:  
            value_status = "High 🔵"  
        elif value_last < 0.5 * value_ma20:  
            value_status = "Low 🔴"  

        fib = get_fib_levels(df)  

        # Peluang TP masuk akal
        peluang_manual = 0
        if ma_status == "Above MA60":
            peluang_manual += 25
        if 55 <= rsi_val <= 75:
            peluang_manual += 20
        elif 50 <= rsi_val < 55:
            peluang_manual += 15
        elif 75 < rsi_val <= 80:
            peluang_manual += 10
        if vol_status == "High 🔵":
            peluang_manual += 15
        elif vol_status == "Normal ⚪":
            peluang_manual += 8
        else:
            peluang_manual += 3
        if value_last >= 5_000_000_000:
            peluang_manual += 10
        elif value_last >= 2_500_000_000:
            peluang_manual += 5
        if fib["fib_618"] <= last_close <= fib["fib_50"]:
            peluang_manual += 30
        elif fib["fib_50"] < last_close <= fib["fib_786"]:
            peluang_manual += 15
        peluang_manual = min(max(peluang_manual, 0), 100)

        ml_3d = round(peluang_manual * 0.35 + 5, 2)
        ml_1y = round(peluang_manual * 0.9 + 5, 2)

        data = {  
            "symbol": symbol,  
            "close": round(last_close, 2),  
            "ma60": round(ma60, 2),  
            "rsi": round(rsi_val, 2),  
            "ma_status": ma_status,  
            "vol_last": round(vol_last),  
            "vol_status": vol_status,  
            "value_last": value_last,  
            "value_status": value_status,  
            "fib_786": fib["fib_786"],  
            "fib_618": fib["fib_618"],  
            "fib_50": fib["fib_50"],  
            "tp_21": fib["tp_21"],  
            "peluang_manual": peluang_manual,  
            "ml_3d": ml_3d,  
            "ml_1y": ml_1y  
        }  

        return data  

    except Exception as e:  
        print(f"{symbol} ❌ Error: {e}")  
        return None

# =====================================================
# Format output untuk Telegram
# =====================================================
def format_output(data):
    if not data:
        return "❌ Tidak ada data"

    vol_m = f"{data['vol_last']/1_000_000:.2f}M"  
    value_fmt = f"{data['value_last']:,}"  

    msg = (  
        f"📊 {data['symbol']} - TF 1d\n"  
        f"Harga : {data['close']}\n"  
        f"MA60  : {data['ma60']} ({'🟢' if data['ma_status']=='Above MA60' else '🔴'})\n"  
        f"RSI   : {data['rsi']}\n"  
        f"Volume: {vol_m} ({data['vol_status']})\n"  
        f"Value : {value_fmt} ({data['value_status']})\n\n"  
        f"📌 Fibonacci (3mo):\n"  
        f"50%   : {data['fib_50']}\n"  
        f"61.8% : {data['fib_618']}\n"  
        f"78.6% : {data['fib_786']}\n"  
        f"TP -21%: {data['tp_21']}\n\n"  
        f"🚀 Peluang Naik ke TP (Manual): {data['peluang_manual']}%\n\n"  
        f"🤖 Machine Learning Probability\n"  
        f"• TP 10% (3 Hari): {data['ml_3d']}%\n"  
        f"• TP 10% (1 Tahun): {data['ml_1y']}%"  
    )  
    return msg
