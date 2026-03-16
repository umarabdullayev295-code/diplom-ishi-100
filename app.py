"""
app.py — Videodan O'zbek Tilidagi Matn va Audio Qidiruv Tizimi
============================================================
Muallif: AI Assistant
Texnologiyalar: Streamlit, faster-whisper, sentence-transformers, FAISS, moviepy
"""

import streamlit as st
import os
import tempfile
import time
from pathlib import Path

# --- Ilovani Sozlash ---
st.set_page_config(
    page_title="🎬 Video AI Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Premium Dark UI
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;600&display=swap');

:root {
    --primary: var(--primary-color);
    --glass-bg: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.1);
}

html, body, [class*="css"] {
    font-family: 'Outfit', 'Inter', sans-serif !important;
}

/* ── Glow Effects ── */
.glow-text {
    text-shadow: 0 0 15px rgba(124, 92, 191, 0.3);
}

/* ── Sarlavha ── */
.main-header {
    text-align: center;
    padding: 3rem 0 2rem;
    background: radial-gradient(circle at center, rgba(124, 92, 191, 0.05) 0%, transparent 70%);
}
.main-header h1 {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--primary-color) 0%, #a371f7 50%, #58a6ff 100%);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 5s ease-in-out infinite;
    letter-spacing: -1.5px;
    margin: 0;
}
.main-header p {
    color: var(--text-color);
    opacity: 0.7;
    font-size: 1.1rem;
    margin-top: 0.6rem;
    font-weight: 400;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

@keyframes shimmer {
    0% { background-position: 0% 50%; opacity: 0.9; }
    50% { background-position: 100% 50%; opacity: 1; }
    100% { background-position: 0% 50%; opacity: 0.9; }
}

/* ── Premium Cards ── */
.result-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    backdrop-filter: blur(10px);
}
.result-card:hover {
    border-color: var(--primary-color);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transform: translateY(-5px) scale(1.01);
}

/* ── Badges ── */
.score-badge {
    padding: 0.3rem 0.9rem;
    border-radius: 30px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.score-high   { background: rgba(63, 185, 80, 0.1); color: #3fb950; border: 1px solid rgba(63, 185, 80, 0.2); }
.score-mid    { background: rgba(210, 153, 34, 0.1); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.2); }
.score-low    { background: rgba(248, 81, 73, 0.1); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.2); }

.time-badge {
    background: var(--background-color);
    color: var(--primary-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 0.4rem 0.8rem;
    font-family: 'Outfit', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background-image: linear-gradient(180deg, var(--secondary-background-color) 0%, var(--background-color) 100%);
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    background: linear-gradient(135deg, var(--primary-color), #7c5cbf) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(124, 92, 191, 0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(124, 92, 191, 0.4) !important;
}

/* ── Engine Badge ── */
.engine-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    background: var(--secondary-background-color);
    border: 1px solid var(--primary-color);
    border-radius: 40px;
    padding: 0.4rem 1.2rem;
    font-size: 0.9rem;
    color: var(--primary-color);
    font-weight: 700;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(88, 166, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }
}

/* ── Stats ── */
.stat-item {
    background: var(--secondary-background-color);
    border-radius: 20px;
    padding: 1.2rem;
    border: 1px solid rgba(128,128,128,0.1);
}
.stat-value { font-size: 1.8rem; font-weight: 800; color: var(--primary-color); }

/* ── Search Highlight ── */
mark {
    background: rgba(255, 235, 59, 0.3);
    color: inherit;
    padding: 0.1rem 0.2rem;
    border-radius: 4px;
    border-bottom: 2px solid #ffeb3b;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "stt_engine": None,
        "search_engine": None,
        "segments": [],
        "video_path": None,
        "video_name": None,
        "index_built": False,
        "processing": False,
        "play_timestamp": 0,
        "last_results": [],
        "engine_name": "",
        "video_duration": 0,
        "elevenlabs_key": "sk_6bdf3d8d457b4daf443e8afe137c86a301954b3df9456ee2",
        "whisper_model": "medium",
        "target_lang": "uz",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔍 AI Media Search</h1>
    <p>Video va audio ichidan matn orqali aqlli qidiruv tizimi</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — Sozlamalar va Video yuklash
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Tizim Sozlamalari")
    st.markdown("---")

    # --- Til Tanlash ---
    with st.expander("🌐 Til va Hudud", expanded=True):
        lang_choice = st.selectbox(
            "Media tili:",
            ["O'zbekcha", "Russian", "English", "Turkish"],
            index=0
        )
        lang_map = {"O'zbekcha": "uz", "Russian": "ru", "English": "en", "Turkish": "tr"}
        st.session_state.target_lang = lang_map[lang_choice]

    # --- AI Engine sozlamalari ---
    with st.expander("🤖 AI Dvigatel", expanded=True):
        default_engine_idx = 0 if st.session_state.target_lang == "uz" else 1
        
        engine_choice = st.selectbox(
            "Transkripsiya modeli:",
            ["O'zbek AI Model (Pro)", "Whisper (Asosiy)"],
            index=default_engine_idx,
            help="O'zbek tili uchun 'Pro' tavsiya etiladi. Boshqa tillar uchun 'Asosiy' model ishonchliroq.",
        )

        if engine_choice == "O'zbek AI Model (Pro)":
            if st.session_state.target_lang != "uz":
                st.warning("⚠️ Bu model o'zbek tili uchun optimallashgan.")
            else:
                st.success("✨ Pro model faol. Yuqori aniqlik kafolatlanadi.")


        else:
            st.session_state.whisper_model = st.selectbox(
                "Whisper model hajmi:",
                ["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                index=["tiny", "base", "small", "medium", "large-v2", "large-v3"].index(
                    st.session_state.whisper_model
                ),
                help="Kattaroq model = aniqroq natija, lekin sekinroq",
            )
            st.info("💡 O'zbek tili uchun `medium` yoki `large-v2` tavsiya etiladi.")

    st.markdown("---")

    # --- Media Yuklash ---
    st.markdown("### 📹 Media Yuklash")
    uploaded_video = st.file_uploader(
        "Video yoki Audio fayl tanlang:",
        type=["mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a", "ogg", "flac"],
        help="Video hamda faqat audio (mp3, wav, m4a) formatlar qo'llab-quvvatlanadi",
    )

    if uploaded_video:
        # Faylni barqaror temp papkada saqlash
        temp_dir = tempfile.gettempdir()
        temp_video_path = os.path.join(temp_dir, f"video_ai_{uploaded_video.name}")

        # Agar fayl nomi o'zgargan bo'lsa yoki fayl mavjud bo'lmasa, qayta saqlaymiz
        if (
            st.session_state.video_name != uploaded_video.name
            or not os.path.exists(temp_video_path)
            or os.path.getsize(temp_video_path) == 0
        ):
            uploaded_video.seek(0)
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_video.read())

        # Yangi video yoki o'zgartirish holatida tasdiqlash tugmasi
        if st.session_state.video_path != temp_video_path:
            if st.button("🚀 Videoni Qayta Ishlash", use_container_width=True):
                st.session_state.video_path = temp_video_path
                st.session_state.video_name = uploaded_video.name
                st.session_state.segments = []
                st.session_state.index_built = False
                st.session_state.last_results = []
                st.session_state.play_timestamp = 0
                st.session_state.processing = True
                st.rerun()

        elif st.session_state.index_built:
            st.success(f"✅ Tayyor: **{uploaded_video.name}**")
            if st.session_state.segments:
                seg_count = len(st.session_state.segments)
                dur = st.session_state.video_duration
                m, s = divmod(int(dur), 60)
                st.markdown(f"""
                <div class="stat-grid">
                    <div class="stat-item">
                        <div class="stat-value">{seg_count}</div>
                        <div class="stat-label">Segment</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{m}:{s:02d}</div>
                        <div class="stat-label">Davomiylik</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#8b949e; font-size:0.78rem;">
        🇺🇿 O'zbek AI Qidiruv Tizimi<br>
        <span style="color:#444">Python · Whisper · FAISS · Streamlit</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VIDEO QAYTA ISHLASH
# ─────────────────────────────────────────────
if st.session_state.processing and st.session_state.video_path:
    st.session_state.processing = False
    video_path = st.session_state.video_path

    progress_container = st.container()
    with progress_container:
        st.markdown("### ⚙️ Qayta Ishlash Bosqichlari")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # ── Qadam 1: Video ma'lumotlari ──
        status_text.markdown("**1/4** 📋 Video ma'lumotlari o'qilmoqda...")
        progress_bar.progress(10)
        from video_processor import get_video_info
        info = get_video_info(video_path)
        st.session_state.video_duration = info.get("duration_sec", 0)
        time.sleep(0.3)

        # ── Qadam 2: Audio ajratish ──
        status_text.markdown("**2/4** 🔊 Audio ajratilmoqda (Tezkor rejim)...")
        progress_bar.progress(25)
        from video_processor import extract_audio
        audio_path = extract_audio(video_path, format="mp3", sample_rate=16000)

        if not audio_path:
            st.error("❌ Audio ajratib bo'lmadi. Video fayldа audio trek mavjudligini tekshiring.")
            st.stop()

        progress_bar.progress(40)

        # ── Qadam 3: Nutqni matnga o'tkazish ──
        status_text.markdown("**3/4** 🧠 Nutq matnga o'tkazilmoqda ...")
        progress_bar.progress(45)

        from speech_to_text import SpeechToText
        stt = SpeechToText(
            whisper_model_size=st.session_state.whisper_model,
            language=st.session_state.target_lang,
            use_api=(engine_choice in ["O'zbek AI Model (Pro)"]),
            elevenlabs_api_key=st.session_state.elevenlabs_key or None,
        )
        st.session_state.stt_engine = stt
        st.session_state.engine_name = stt.get_engine_name()

        segments = stt.transcribe(audio_path)
        st.session_state.segments = segments

        # Temp audio faylni o'chirish
        from utils import cleanup_file
        cleanup_file(audio_path)

        progress_bar.progress(70)

        if not segments:
            st.warning("⚠️ Audio transkripsiya natijalari bo'sh. Boshqa model yoki fayl sinab ko'ring.")
            st.stop()

        # ── Qadam 4: Semantik indeks yaratish ──
        status_text.markdown(f"**4/4** 🔍 Semantik qidiruv indeksi yaratilmoqda ({len(segments)} segment)...")
        progress_bar.progress(80)

        from semantic_search import SemanticSearch
        search_engine = SemanticSearch()
        count = search_engine.add_transcripts(segments)
        st.session_state.search_engine = search_engine
        st.session_state.index_built = True

        progress_bar.progress(100)
        status_text.markdown(f"✅ **Tayyorlandi!** {count} segment indekslandi.")
        time.sleep(1)

    st.rerun()

# ─────────────────────────────────────────────
# ASOSIY QISM: Qidiruv va Natijalar
# ─────────────────────────────────────────────
if not st.session_state.index_built:
    # Xush kelibsiz sahifasi
    st.markdown("""
    <div class="info-banner">
        <h3>👈 Boshlash uchun video yuklang</h3>
        <p>Chap paneldan video faylni yuklang va "Videoni Qayta Ishlash" tugmasini bosing</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="result-card" style="text-align:center">
            <div style="font-size:2rem">🎬</div>
            <div style="font-weight:600;margin:0.5rem 0">Video Yuklash</div>
            <div style="color:#8b949e;font-size:0.85rem">MP4, MOV, AVI, MKV formatlar</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="result-card" style="text-align:center">
            <div style="font-size:2rem">🧠</div>
            <div style="font-weight:600;margin:0.5rem 0">AI Tahlil</div>
            <div style="color:#8b949e;font-size:0.85rem">Whisper + Semantik qidiruv</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="result-card" style="text-align:center">
            <div style="font-size:2rem">🔍</div>
            <div style="font-weight:600;margin:0.5rem 0">Qidiruv</div>
            <div style="color:#8b949e;font-size:0.85rem">Matn yoki audio orqali</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # ── Qidiruv va Video ──
    col_search, col_video = st.columns([1, 1], gap="large")

    # ─── QIDIRUV USTUNI ───
    with col_search:
        st.markdown("### 🔍 Qidiruv")

        # Engine ko'rsatkichi
        st.markdown(f"""
        <div class="engine-badge">
            🤖 {st.session_state.engine_name}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        # Qidiruv rejimi
        search_mode = st.radio(
            "Qidiruv turi:",
            ["📝 Matn orqali", "🎤 Audio orqali"],
            horizontal=True,
        )
        st.markdown("")

        query_text = ""
        perform_search = False

        # ── Matn qidiruv ──
        if search_mode == "📝 Matn orqali":
            query_text = st.text_input(
                "So'rov kiriting:",
                placeholder="Misol: qush, mashina o'qitish...",
                key="text_query",
            )
            top_k = st.slider("Nechta natija ko'rsatilsin:", 1, 10, 3)

            if st.button("🔍 Qidirish", use_container_width=True, type="primary"):
                if query_text.strip():
                    perform_search = True
                else:
                    st.warning("⚠️ Qidiruv matni kiriting.")

        # ── Audio qidiruv ──
        else:
            st.info("🎤 Audio yozuv yoki ovozli so'rovingizni yuklang.")
            audio_query = st.file_uploader(
                "Audio fayl yuklang:",
                type=["mp3", "wav", "ogg", "m4a"],
                key="audio_query_file",
            )
            top_k = st.slider("Nechta natija ko'rsatilsin:", 1, 10, 3, key="top_k_audio")

            if audio_query:
                if st.button("🔍 Audio orqali Qidirish", use_container_width=True, type="primary"):
                    with st.spinner("Audio qayta ishlanmoqda..."):
                        tmp_f = tempfile.NamedTemporaryFile(
                            delete=False, suffix=f".{audio_query.name.split('.')[-1]}"
                        )
                        tmp_f.write(audio_query.read())
                        tmp_f.close()

                        stt = st.session_state.stt_engine
                        if stt is None:
                            from speech_to_text import SpeechToText
                            stt = SpeechToText(
                                whisper_model_size=st.session_state.whisper_model,
                                language="uz",
                                elevenlabs_api_key=st.session_state.elevenlabs_key or None,
                            )
                            st.session_state.stt_engine = stt

                        q_segments = stt.transcribe(tmp_f.name)
                        from utils import cleanup_file
                        cleanup_file(tmp_f.name)

                        if q_segments:
                            query_text = " ".join(s["text"] for s in q_segments)
                            st.success(f"🎤 Tanilgan matn: *{query_text}*")
                            perform_search = True
                        else:
                            st.error("❌ Audioni matnga o'tkazib bo'lmadi.")

        # ── Natijalarni ko'rsatish ──
        if perform_search and query_text.strip():
            with st.spinner("Qidirilmoqda..."):
                # So'zma-so'z segmentlar uchun context_window qo'shish natijani o'qishni osonlashtiradi
                results = st.session_state.search_engine.search_with_context(
                    query_text.strip(), top_k=top_k, context_window=5
                )
            
            st.session_state.last_results = results
            
            # Agar kamida bitta natija bo'lsa, avtomatik birinchi natija vaqtiga o'tkazish
            if results and len(results) > 0:
                st.session_state.play_timestamp = int(results[0]["start"])
                st.rerun()

        if st.session_state.last_results:
            st.markdown(f"#### 📋 Natijalar — {len(st.session_state.last_results)} ta topildi")

            for i, res in enumerate(st.session_state.last_results):
                score = res["score"]
                from utils import format_time, score_to_percent, get_similarity_label, highlight_text
                label, _ = get_similarity_label(score)

                score_css = "score-high" if score >= 0.65 else ("score-mid" if score >= 0.4 else "score-low")
                start_fmt = format_time(res["start"])
                end_fmt = format_time(res["end"])

                # Contextual text bo'lsa uni ishlatamiz (so'zma-so'z qidiruvda readability uchun)
                display_text = res.get("context_text", res["text"])
                highlighted = highlight_text(display_text, query_text)

                st.markdown(f"""
                <div class="result-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem">
                        <span style="color:#8b949e;font-size:0.85rem">№{i+1}</span>
                        <span class="score-badge {score_css}">{score_to_percent(score)} — {label}</span>
                    </div>
                    <div style="font-size:0.95rem;line-height:1.6;margin-bottom:0.7rem">{highlighted}</div>
                    <span class="time-badge">⏱ {start_fmt} → {end_fmt}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"▶ {start_fmt} dan ijro etish", key=f"play_{i}_{start_fmt}"):
                    st.session_state.play_timestamp = int(res["start"])
                    st.rerun()

        elif st.session_state.last_results == [] and perform_search:
            st.markdown("""
            <div class="result-card" style="text-align:center;padding:2rem">
                <div style="font-size:2rem">🔍</div>
                <div style="color:#8b949e">Bu so'rov uchun natija topilmadi.</div>
                <div style="color:#444;font-size:0.85rem;margin-top:0.4rem">Boshqa kalit so'zlar bilan urinib ko'ring.</div>
            </div>
            """, unsafe_allow_html=True)

    # ─── MEDIA USTUNI ───
    with col_video:
        st.markdown("### 🎬 Media Player")

        if st.session_state.video_path and os.path.exists(st.session_state.video_path):
            start_time = st.session_state.get("play_timestamp", 0)
            
            # Subtitrlarni tayyorlash (agar mavjud bo'lsa)
            vtt_subs = None
            if st.session_state.get("segments"):
                from utils import segments_to_vtt
                vtt_text = segments_to_vtt(st.session_state.segments)
                # Streamlit v1.34+ expects a dictionary for labels or a direct string
                vtt_subs = {"Subtitrlar (AI)": vtt_text}

            try:
                ext = os.path.splitext(st.session_state.video_path)[1].lower()
                is_audio = ext in [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
                
                if is_audio:
                    # Audio fayllar uchun maxsus (subtitr ishlashi uchun video component qilib ko'ramiz
                    # yoki standart audio component ishlatamiz)
                    try:
                        st.video(st.session_state.video_path, start_time=start_time, subtitles=vtt_subs)
                    except Exception:
                        st.audio(st.session_state.video_path, start_time=start_time)
                        if start_time > 0:
                            st.info("Pleyer kerakli joydan davom etmoqda.")
                else:
                    # Video elementi start time va subtitr bilan
                    st.video(st.session_state.video_path, start_time=start_time, subtitles=vtt_subs)
            except Exception as e:
                st.error(f"Media yuklashda xato: {e}")

        # ── Transkript ──
        st.markdown("---")
        with st.expander("📜 To'liq Transkript", expanded=False):
            if st.session_state.segments:
                # SRT yuklab olish tugmasi
                from utils import segments_to_srt, segments_to_text
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    srt_content = segments_to_srt(st.session_state.segments)
                    st.download_button(
                        "⬇ SRT yuklab olish",
                        data=srt_content,
                        file_name="transkript.srt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                with col_dl2:
                    txt_content = segments_to_text(st.session_state.segments)
                    st.download_button(
                        "⬇ TXT yuklab olish",
                        data=txt_content,
                        file_name="transkript.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                st.markdown("")
                from utils import format_time
                for seg in st.session_state.segments:
                    ts = format_time(seg["start"])
                    st.markdown(
                        f'<div class="transcript-line"><span class="time-badge">{ts}</span>'
                        f' &nbsp;{seg["text"]}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Transkript mavjud emas.")

        # ── Video statistika ──
        if st.session_state.segments:
            st.markdown("---")
            st.markdown("#### 📊 Statistika")
            total_words = sum(len(s["text"].split()) for s in st.session_state.segments)
            dur = st.session_state.video_duration
            m, s_sec = divmod(int(dur), 60)

            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{len(st.session_state.segments)}</div>
                    <div class="stat-label">Segmentlar</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{total_words}</div>
                    <div class="stat-label">So'zlar</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{m}:{s_sec:02d}</div>
                    <div class="stat-label">Davomiylik</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
