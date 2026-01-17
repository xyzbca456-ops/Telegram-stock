# 📈 Telegram Stock Screener Bot

Bot Telegram untuk screening saham IDX berbasis:
- RSI
- MA60
- Fibonacci 3 bulan
- Probabilitas Manual
- Probabilitas Machine Learning (ML)
- Volume & likuiditas

Dibangun dengan:
- Python
- python-telegram-bot v20+
- yfinance
- Flask (untuk server di Render)

---

## 🚀 Fitur Bot

### **1. /start**
Menampilkan menu bantuan & daftar perintah.

### **2. /scan SYMBOL**
Contoh:
```
/scan BBRI.JK
```
Menampilkan:
- Harga sekarang  
- RSI  
- Status MA  
- Fibonacci  
- Probabilitas manual  
- Probabilitas ML (3 hari & 1 tahun)

---

### **3. /rekomendasi**
Menampilkan 15 saham terbaik untuk day trade:
- RSI 55–75  
- Harga di atas MA60  
- Urut berdasarkan peluang + volume

---

### **4. /swing**
Menampilkan 10 saham terbaik untuk swing trading:
- RSI 35–50  
- Harga di bawah MA60  
- Urut berdasarkan peluang + volume

---

## 📁 Struktur Folder

```
/telegram-stock-screener
│── telegram_bot.py
│── screener.py
│── issi_symbols.py
│── ml_predictor.py
│── ml_prob_model.py
│── model_training.py   (opsional)
│── server.py
│── requirements.txt
└── README.md
```

---

## 🟦 Deploy ke Render

### 1. Upload semua file ke GitHub  
Buat repo:
```
telegram-stock-screener
```

### 2. Buat Web Service di Render  
- New → Web Service  
- Deploy from GitHub  
- Pilih repo `telegram-stock-screener`  
- **Runtime: Python**  
- **Start Command:**
```
python telegram_bot.py
```

### 3. Tambah _Environment Variable_
Nama:  
```
BOT_TOKEN
```
Value:  
```
<token telegram kamu>
```

### 4. Tambah Health Check  
Path:
```
/
```

Port:
```
10000
```

### 5. Deploy  
Render akan:
- Menjalankan server.py untuk health-check  
- Menjalankan telegram_bot.py untuk polling  
- Bot hidup 24 jam nonstop  

---

## 💡 Troubleshooting
Jika bot tidak merespon:
- Cek logs Render  
- Pastikan BOT_TOKEN benar  
- Pastikan semua file sudah upload  
- Pastikan requirements.txt lengkap  

---

# 🎉 Selesai!
Bot kamu siap dipakai 24 jam.
