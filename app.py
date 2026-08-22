import hashlib
from datetime import datetime

import streamlit as st

from src.database import create_table, save_chunks, get_chunks, delete_pdf
from src.chunker import create_chunks
from src.pdf_reader import extract_text
from src.retrieval import search_chunks, answer_question, question_kind
from src.styles import apply_styles


st.set_page_config(
    page_title="CampusAI",
    page_icon="🎓",
    layout="wide",
)

PROCESSING_VERSION = 8
MAX_FILE_SIZE_MB = 200
MODEL_LABEL = "phi-4-mini"

EXAMPLE_QUESTIONS = [
    "Tıbbi Mikrobiyoloji finali ne zaman?",
    "Bilgisayar Mühendisliği dersleri kimler tarafından veriliyor?",
    "Anatomi dersinin dersliği neresi?",
    "Bahar dönemi bütünleme sınavları ne zaman?",
]

KIND_ICON = {
    "courses": "📚",
    "teacher": "👤",
    "room": "📍",
    "date": "📅",
    None: "💬",
}

KIND_LABEL = {
    "courses": "Ders listesi",
    "teacher": "Öğretim üyesi",
    "room": "Derslik",
    "date": "Sınav tarihi",
    None: "Genel soru",
}

apply_styles()
create_table()


# =========================================================
# SESSION STATE
# =========================================================

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "history" not in st.session_state:
    st.session_state.history = []

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "question_value" not in st.session_state:
    st.session_state.question_value = ""


def file_signature(uploaded_file):
    """Dosya adı + boyut yerine içerik hash'i kullanır."""
    data = uploaded_file.getvalue()
    digest = hashlib.sha256(data).hexdigest()[:16]
    return PROCESSING_VERSION, uploaded_file.name, uploaded_file.size, digest


def set_question(text):
    st.session_state.question_value = text


def clear_question():
    st.session_state.question_value = ""
    st.session_state.last_question = ""


def force_refresh():
    st.session_state.last_question = ""


def document_counts():
    counts = {}
    for row in get_chunks():
        if isinstance(row, (tuple, list)) and row:
            counts[row[0]] = counts.get(row[0], 0) + 1
    return counts


def relative_time(dt):
    if dt.date() == datetime.now().date():
        return f"Bugün {dt.strftime('%H:%M')}"
    return dt.strftime("%d %b")


# =========================================================
# NAVBAR
# =========================================================

st.markdown(
    """
    <div class="ca-navbar">
        <div class="ca-navbar-inner">
            <div class="ca-nav-brand">
                <div class="ca-nav-logo">CA</div>
                <div class="ca-nav-word">CampusAI</div>
            </div>
            <div class="ca-nav-links">
                <a href="#soru">Soru Sor</a>
                <a href="#ozellikler">Özellikler</a>
            </div>
            <div class="ca-nav-tag">🇹🇷 TR</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="ca-hero">
        <div class="ca-badge">🎓 Ücretsiz · Kurulumsuz · Verileriniz yerelde kalır</div>
        <h1>Ders programınızı<br><span class="ca-grad">saniyeler içinde</span> sorun.</h1>
        <div class="ca-hero-sub">
            PDF ders programlarınızı yükleyin; sınav tarihi, saat, derslik ve öğretim üyesi
            bilgisini CampusAI sizin için bulsun.
        </div>
        <a class="ca-cta" href="#soru">🎓 Belge Yükle ve Sor</a>
        <div class="ca-hero-note">🔒 Belgeleriniz bu cihazda kalır, dışarıya gönderilmez.</div>
    </div>
    <div id="soru"></div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ANA PANEL — BELGE + SORU  /  YANIT
# =========================================================

left, right = st.columns([1, 1.15], gap="large")

with left:
    with st.container(border=True):
        st.markdown(
            """
            <div class="ca-card-header">
                <div>
                    <div class="ca-card-eyebrow">Adım 1</div>
                    <div class="ca-card-title">📄 Belgelerinizi Yükleyin</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"Ders, öğretim üyesi, sınav tarihi, saat ve derslik bilgisi içeren PDF'leri "
            f"yükleyin. Dosya başına en fazla {MAX_FILE_SIZE_MB} MB."
        )

        uploaded_files = st.file_uploader(
            "PDF yükleyin",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        counts = document_counts()

        if not counts:
            st.markdown(
                '<div class="ca-empty-state">Henüz belge yüklenmedi.</div>',
                unsafe_allow_html=True,
            )
        else:
            for pdf_name, chunk_count in sorted(counts.items()):
                doc_col, action_col = st.columns([5, 1])
                with doc_col:
                    st.markdown(
                        f"""
                        <div class="ca-doc-item">
                            <div class="ca-doc-name">{pdf_name}</div>
                            <div class="ca-doc-badge">{chunk_count} chunk</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with action_col:
                    if st.button("🗑", key=f"delete_{pdf_name}", help=f"{pdf_name} dosyasını kaldır"):
                        delete_pdf(pdf_name)
                        st.session_state.processed_files = {
                            sig for sig in st.session_state.processed_files if sig[1] != pdf_name
                        }
                        st.rerun()

    with st.container(border=True):
        st.markdown(
            """
            <div class="ca-card-header">
                <div>
                    <div class="ca-card-eyebrow">Adım 2</div>
                    <div class="ca-card-title">💬 Sorunuzu Yazın</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        question = st.text_input(
            "Sorunuzu yazın",
            key="question_value",
            placeholder="Örn. Tıbbi Mikrobiyoloji finali ne zaman?",
            label_visibility="collapsed",
        )

        st.caption("Örnekler")
        chip_rows = [EXAMPLE_QUESTIONS[:2], EXAMPLE_QUESTIONS[2:]]
        for row in chip_rows:
            cols = st.columns(len(row))
            for col, example in zip(cols, row):
                with col:
                    st.button(
                        example,
                        key=f"chip_{example}",
                        on_click=set_question,
                        args=(example,),
                        use_container_width=True,
                    )

        st.button("↺ Soruyu Temizle", key="reset_question", on_click=clear_question)


# =========================================================
# PDF İŞLEME
# =========================================================

if uploaded_files:
    for uploaded_file in uploaded_files:
        signature = file_signature(uploaded_file)

        if signature in st.session_state.processed_files:
            continue

        with st.spinner(f"📄 {uploaded_file.name} işleniyor..."):
            try:
                text = extract_text(uploaded_file)

                if not text.strip():
                    st.error(f"{uploaded_file.name}: PDF'den metin okunamadı.")
                    continue

                chunks = create_chunks(text)

                if not chunks:
                    st.error(f"{uploaded_file.name}: İşlenebilir metin bulunamadı.")
                    continue

                delete_pdf(uploaded_file.name)
                save_chunks(uploaded_file.name, chunks)

                st.session_state.processed_files.add(signature)

                st.success(f"✅ {uploaded_file.name} başarıyla yüklendi ({len(chunks)} chunk).")

            except Exception as exc:
                st.error(f"{uploaded_file.name} işlenirken hata oluştu: {exc}")


# =========================================================
# SORU CEVAP — sağ panel
# =========================================================

question = st.session_state.question_value

if question and question.strip():
    if question != st.session_state.last_question:
        with st.spinner("🤖 CampusAI düşünüyor..."):
            error = None
            try:
                answer = answer_question(question)
            except Exception as exc:
                answer = None
                error = exc

        results = search_chunks(question, limit=4) if error is None else []

        st.session_state.history.insert(
            0,
            {
                "question": question,
                "answer": answer,
                "error": error,
                "results": results,
                "kind": question_kind(question),
                "asked_at": datetime.now(),
            },
        )
        st.session_state.last_question = question

    latest = st.session_state.history[0]
    status_class = "ca-status-error" if latest["error"] is not None else "ca-status-ready"
    status_text = "Hata" if latest["error"] is not None else "Hazır"
else:
    latest = None
    status_class = "ca-status-idle"
    status_text = "Bekleniyor"

with right:
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="ca-card-header">
                <div>
                    <div class="ca-card-eyebrow">Sonuç</div>
                    <div class="ca-card-title">🤖 CampusAI Yanıtı</div>
                </div>
                <div class="ca-status-pill {status_class}">
                    <span class="ca-status-dot"></span>{status_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if latest is None:
            st.markdown(
                '<div class="ca-empty-state-lg">💬 Bir soru yazın veya sol taraftaki '
                "örneklerden birini seçin.</div>",
                unsafe_allow_html=True,
            )
        elif latest["error"] is not None:
            st.error("CampusAI yanıtı oluşturulurken bir hata oluştu.")
            with st.expander("Teknik detay"):
                st.code(str(latest["error"]))
        else:
            st.markdown(
                f'<div class="ca-answer-body">{latest["answer"]}</div>',
                unsafe_allow_html=True,
            )

            st.button("🔁 Yeniden Sor", key="force_refresh", on_click=force_refresh)

            if latest["results"]:
                with st.expander("🔎 Kullanılan Bilgiler"):
                    for score, pdf_name, chunk_no, content in latest["results"]:
                        st.markdown(
                            f"""
                            <div class="ca-source-pill">
                                <span class="ca-source-name">{pdf_name} · Chunk {chunk_no}</span>
                                <span class="ca-source-score">skor {score}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.caption(content)

        st.caption("Yanıtlar yalnızca yüklediğiniz belgelere dayanır.")


# =========================================================
# SON SORULAR
# =========================================================

if st.session_state.history:
    st.markdown('<div id="son-sorular"></div>', unsafe_allow_html=True)

    head_col, action_col = st.columns([5, 1])
    with head_col:
        st.markdown(
            '<div class="ca-card-eyebrow" style="margin-top:2.4rem;">Geçmiş</div>'
            '<div class="ca-card-title" style="margin-bottom:0.9rem;">🕘 Son Sorular</div>',
            unsafe_allow_html=True,
        )
    with action_col:
        st.markdown('<div style="margin-top:2.4rem;"></div>', unsafe_allow_html=True)
        if st.button("🗑 Geçmişi Temizle", key="clear_history"):
            st.session_state.history = []
            st.session_state.last_question = ""
            st.rerun()

    with st.container(border=True):
        for item in st.session_state.history[:8]:
            icon = KIND_ICON.get(item["kind"], "💬")
            label = KIND_LABEL.get(item["kind"], "Genel soru")
            st.markdown(
                f"""
                <div class="ca-list-row">
                    <div class="ca-list-icon">{icon}</div>
                    <div>
                        <div class="ca-list-title">{item['question']}</div>
                        <div class="ca-list-sub">{label}</div>
                    </div>
                    <div class="ca-list-time">{relative_time(item['asked_at'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# ÖZELLİKLER
# =========================================================

st.markdown('<div id="ozellikler"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ca-section-title" style="margin-top:3.2rem;">CampusAI neler sunar?</div>',
    unsafe_allow_html=True,
)

features = [
    ("⚡", "Hızlı Yanıt", "Program, hoca, derslik ve tarih soruları önce yapısal tablo eşleştirmesiyle cevaplanır; yapay zekâ yalnızca gerektiğinde devreye girer."),
    ("📎", "Çoklu Belge", "Birden fazla PDF'yi aynı anda yükleyin, CampusAI hepsini birlikte tarar."),
    ("🔒", "Yerelde Çalışır", "Belgeleriniz ve sorularınız bu cihazda kalır; yanıtlar yerel bir modelle üretilir."),
    ("🎓", "Ücretsiz", "Kayıt, abonelik veya reklam yok."),
]

feature_cols = st.columns(4, gap="medium")
for col, (icon, title, desc) in zip(feature_cols, features):
    with col:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="ca-feature-icon">{icon}</div>
                <div class="ca-feature-title">{title}</div>
                <div class="ca-feature-desc">{desc}</div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# GELİŞTİRİCİ PANELİ
# =========================================================

with st.expander("🛠 Geliştirici Paneli"):
    rows = get_chunks()

    pdf_names = {
        row[0]
        for row in rows
        if isinstance(row, (tuple, list)) and len(row) > 0
    }

    st.markdown(
        f"""
        <div class="ca-metric-grid">
            <div class="ca-metric">
                <div class="ca-metric-value">{len(pdf_names)}</div>
                <div class="ca-metric-label">Toplam PDF</div>
            </div>
            <div class="ca-metric">
                <div class="ca-metric-value">{len(rows)}</div>
                <div class="ca-metric-label">Toplam Chunk</div>
            </div>
            <div class="ca-metric">
                <div class="ca-metric-value">{MODEL_LABEL}</div>
                <div class="ca-metric-label">Model</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Ders/hoca/derslik/tarih sorularında önce yapısal tablo eşleştirmesi yapılır; "
        "yalnızca gerekli olduğunda LLM devreye girer."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="ca-footer">
        <div>
            <div class="ca-nav-brand">
                <div class="ca-nav-logo">CA</div>
                <div class="ca-nav-word">CampusAI</div>
            </div>
            <div class="ca-footer-tagline">
                Ders programınızı okuyun, sorun, öğrenin. Belgeleriniz bu cihazda kalır.
            </div>
        </div>
    </div>
    <div class="ca-footer-copy">© 2026 CampusAI. Belgeleriniz yalnızca bu oturumda işlenir.</div>
    """,
    unsafe_allow_html=True,
)