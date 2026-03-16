# 🎬 Videodan O'zbek Tilidagi Matn va Audio Qidiruv Tizimi

**Video AI Search** — Python asosidagi sun'iy intellekt tizimi bo'lib, video fayllar ichidan **o'zbek tilidagi matn yoki audio** orqali aqlli qidiruv amalga oshiradi va ushbu ma'lumotning video vaqt oralig'ini aniq ko'rsatadi.

---

## 🚀 Imkoniyatlar

| Imkoniyat | Tavsif |
|-----------|--------|
| 🎤 Nutq → Matn | Whisper / AI Labs / Muxlisa API |
| 🔍 Semantik Qidiruv | O'zbek tili uchun ko'p tilli model + FAISS |
| 🎬 Video Player | Topilgan joydan o'ynash |
| 📝 Matn Qidiruv | O'zbek tilidagi so'rov |
| 🎙 Audio Qidiruv | Ovozli so'rov yuklab qidiruv |
| 📜 Transkript | SRT va TXT formatda export |
| ⏱ Vaqt belgilari | `0.0 – 3.4: Assalomu alaykum` |
| 🌍 Ko'p tilli | O'zbek, Rus, Ingliz va boshqa tillar |

---

## 📁 Loyiha Strukturasi

```
video_ai_search/
├── app.py                  # Streamlit web interfeys (asosiy)
├── ai_labs_api.py          # AI Labs + Muxlisa API integratsiya
├── speech_to_text.py       # Nutqni matnga o'tkazish (unified)
├── video_processor.py      # Videodan audio ajratish (moviepy)
├── semantic_search.py      # FAISS + sentence-transformers
├── utils.py                # Yordamchi funksiyalar
├── requirements.txt        # Python paketlari
├── .env.example            # API kalitlar namunasi
└── README.md
```

---

## ⚙️ O'rnatish

### 1. Python muhitini yarating

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Paketlarni o'rnating

```bash
pip install -r requirements.txt
```

> **Muhim:** CUDA GPU mavjud bo'lsa, PyTorch CUDA versiyasini o'rnating:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

### 3. (Ixtiyoriy) API kalitlarini sozlang

`.env.example` faylini `.env` nomi bilan nusxalang:

```bash
copy .env.example .env
```

`.env` faylini oching va API kalitlarini kiriting:

```env
AI_LABS_API_KEY=your_ai_labs_key_here
MUXLISA_API_KEY=your_muxlisa_key_here
```

---

## ▶️ Ishga Tushirish

```bash
streamlit run app.py
```

Brauzer avtomatik ochiladi: **http://localhost:8501**

---

## 🔧 Foydalanish

1. **Video yuklash** → Chap paneldan video faylni tanlang (MP4, MOV, AVI, MKV)
2. **AI dvigatel tanlang** → Whisper (offline) yoki API (AI Labs / Muxlisa)
3. **"Videoni Qayta Ishlash"** tugmasini bosing
4. **Qidiruv kiriting** → Matn yoki audio fayl
5. **"Qidirish"** tugmasini bosing
6. **Natijalarni ko'ring** → Vaqt belgilari va video player orqali o'sha joyga o'ting

---

## 🤖 Transkripsiya Dvigatellari

### Whisper (Offline — Internet shart emas)

| Model | Xotira | Tezlik | Aniqlik |
|-------|--------|--------|---------|
| `tiny` | ~1 GB RAM | Juda tez | Past |
| `base` | ~1 GB RAM | Tez | O'rtacha |
| `small` | ~2 GB RAM | O'rtacha | Yaxshi |
| `medium` | ~5 GB RAM | Sek | **Tavsiya (O'zbek)** |
| `large-v2` | ~10 GB RAM | Sekin | Juda yuqori |
| `large-v3` | ~10 GB RAM | Sekin | Eng yuqori |

> O'zbek tili uchun `medium` yoki `large-v2` modeli tavsiya etiladi.

### AI Labs API (Online)

- Sayt: [arilabs.ai](https://arilabs.ai)
- O'zbek tilidagi nutqni aniq taniydi
- API kalitini `.env` ga `AI_LABS_API_KEY=...` sifatida kiriting

### Muxlisa API (Online)

- Sayt: [muxlisa.ai](https://muxlisa.ai)  
- API kalitini `.env` ga `MUXLISA_API_KEY=...` sifatida kiriting

---

## 📦 Asosiy Paketlar

| Paket | Maqsad |
|-------|--------|
| `streamlit` | Web interfeys |
| `moviepy` | Video→Audio ajratish |
| `faster-whisper` | Lokal nutq tanish |
| `sentence-transformers` | Ko'p tilli embedding |
| `faiss-cpu` | Vektor qidiruv |
| `torch` | Deep learning asosi |
| `requests` | API so'rovlar |
| `python-dotenv` | Muhit o'zgaruvchilari |

---

## 🇺🇿 O'zbek Tili Haqida

Tizim o'zbek tilini quyidagi yo'llar bilan qo'llab-quvvatlaydi:

- **Whisper** → `language="uz"` parametri bilan majburiy o'zbek tilida transkripsiya
- **Semantik qidiruv** → `paraphrase-multilingual-MiniLM-L12-v2` modeli 50+ til (o'zbek tilini ham) qo'llab-quvvatlaydi
- **Sinonimlar** → Semantik qidiruv orqali bir xil ma'nodagi so'zlar ham topiladi
- **AI Labs / Muxlisa** → O'zbek tiliga maxsus API'lar

---

## 🛠 Muammolar va Yechimlar

**moviepy o'rnatishda xato:**
```bash
pip install moviepy==1.0.3
```

**FAISS xatosi:**
```bash
pip install faiss-cpu --no-cache-dir
```

**Whisper modeli yuklanmaydi (sekin internet):**  
Bir marta yuklanadi va keshlanadi. Sabr qiling.

**O'zbek tilida transkripsiya noto'g'ri:**  
`large-v2` yoki `large-v3` modeli yaxshiroq natija beradi.

---

## 📄 Litsenziya

MIT License — Erkin foydalanishingiz mumkin.
