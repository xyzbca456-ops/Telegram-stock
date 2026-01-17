from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from screener import get_stock_info, format_output
from issi_symbols import ISSI_BATCHES  # Semua saham IDX
import asyncio
import random

BOT_TOKEN = "8441615696:AAFgW8QUH2mP2yN9Cyr1xYBZb8xHew1WBfI"

# =====================================================
# /start
# =====================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Screener ALPHA Aktif!\n\n"
        "Perintah:\n"
        "• /rekomendasi — Top 15 Day trade\n"
        "• /swing — Top 10 swing (hold 5-10 hari)\n"
        "• /scan SYMBOL — Scan analisa per saham\n\n"
        "Contoh: /scan BBRI.JK",
        parse_mode="Markdown"
    )

# =====================================================
# /scan — menampilkan data lengkap + peluang TP
# =====================================================
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Gunakan: /scan BBRI.JK")
        return

    symbol = context.args[0].upper()  
    await update.message.reply_text(f"⏳ Scanning {symbol}...")  

    data = get_stock_info(symbol)  
    msg = format_output(data)  
    await update.message.reply_text(msg, parse_mode="Markdown")  
    await asyncio.sleep(0.5)

# =====================================================
# Fungsi bantu buat warna probability
# =====================================================
def prob_emoji(value):
    if value >= 70:
        return "🟢"  # sangat besar
    elif value >= 40:
        return "🟡"  # sedang
    else:
        return "🔴"  # kecil

# =====================================================
# Fungsi umum buat rekomendasi / swing
# =====================================================
async def get_top_stocks(update: Update, mode: str):
    """
    mode: "rekomendasi" atau "swing"
    Ambil saham berdasarkan peluang_manual + liquid, tanpa duplikasi
    """
    await update.message.reply_text("⏳ Mengambil data terbaik 🚀⚡...")

    results = []
    for batch in ISSI_BATCHES:
        for sym in batch if isinstance(batch, list) else [batch]:
            info = get_stock_info(sym)  # Fibonacci 3mo sudah default
            if not info:
                continue

            if mode == "rekomendasi" and 55 <= info["rsi"] <= 75 and info["ma_status"]=="Above MA60":
                results.append(info)
            elif mode == "swing" and 35 <= info["rsi"] <= 50 and info["ma_status"]=="Below MA60":
                results.append(info)

    if not results:
        msg_empty = "❌ Tidak ada yang memenuhi filter " + \
                    ("RSI 55–75 + MA🟢" if mode=="rekomendasi" else "Swing (RSI 35–50 + MA🔴)")
        await update.message.reply_text(msg_empty)
        return

    # Shuffle dulu supaya tidak selalu A-Z
    random.shuffle(results)

    # Urutkan berdasarkan peluang_manual + volume (liquid)
    results.sort(key=lambda x: (x["peluang_manual"], x["vol_last"]), reverse=True)

    # Ambil topN unik
    topN = []
    seen_symbols = set()
    limit = 15 if mode=="rekomendasi" else 10

    for s in results:
        if s["symbol"] in seen_symbols:
            continue
        topN.append(s)
        seen_symbols.add(s["symbol"])
        if len(topN) >= limit:
            break

    # Kirim ke Telegram
    for s in topN:
        msg = format_output(s)
        msg += f"\n\n📊 Probabilitas:\n" \
               f"• Manual : {s['peluang_manual']}% {prob_emoji(s['peluang_manual'])}\n" \
               f"• TP 3 Hari : {s['ml_3d']}% {prob_emoji(s['ml_3d'])}\n" \
               f"• TP 1 Tahun: {s['ml_1y']}% {prob_emoji(s['ml_1y'])}"
        await update.message.reply_text(msg, parse_mode="Markdown")
        await asyncio.sleep(0.5)

# =====================================================
# /rekomendasi — Top 15 Day Trade
# =====================================================
async def rekomendasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_top_stocks(update, mode="rekomendasi")

# =====================================================
# /swing — Top 10 Swing
# =====================================================
async def swing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_top_stocks(update, mode="swing")

# =====================================================
# Run Bot
# =====================================================
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))  
    app.add_handler(CommandHandler("scan", scan))  
    app.add_handler(CommandHandler("rekomendasi", rekomendasi))  
    app.add_handler(CommandHandler("swing", swing))  

    print("Bot is running...")  
    app.run_polling()

if __name__ == "__main__":
    run_bot()
