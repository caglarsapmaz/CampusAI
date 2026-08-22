import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650;9..144,800;9..144,900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* =====================================================
           DESIGN TOKENS
           ===================================================== */
        :root {
            --bg: #0a0d13;
            --bg-glow-1: rgba(200, 40, 58, 0.06);
            --bg-glow-2: rgba(90, 110, 160, 0.05);

            --panel: rgba(255, 255, 255, 0.032);
            --panel-strong: rgba(255, 255, 255, 0.06);
            --border: rgba(255, 255, 255, 0.10);
            --border-strong: rgba(255, 255, 255, 0.20);

            --ink: #f3f4f8;
            --ink-muted: #9aa1b2;
            --ink-faint: #666e80;

            --crimson: #e0263f;
            --crimson-strong: #ff3b52;
            --crimson-soft: rgba(224, 38, 63, 0.14);
            --gold: #d7ad5f;
            --success: #3fcf8e;
            --success-soft: rgba(63, 207, 142, 0.14);

            --grad: linear-gradient(100deg, var(--crimson-strong), var(--gold));

            --font-display: 'Fraunces', Georgia, serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, monospace;

            --radius-lg: 20px;
            --radius-md: 13px;
            --radius-sm: 9px;

            --content-w: 1180px;
        }

        html, body, [class*="css"] { font-family: var(--font-body); font-weight: 500; }

        /* =====================================================
           APP SHELL
           ===================================================== */
        .stApp {
            background:
                radial-gradient(circle at 10% 4%, var(--bg-glow-1), transparent 32%),
                radial-gradient(circle at 92% 8%, var(--bg-glow-2), transparent 34%),
                var(--bg);
            color: var(--ink);
        }

        header[data-testid="stHeader"] { display: none; }
        #MainMenu, footer[data-testid="stBottom"] > div { visibility: hidden; }

        .block-container {
            max-width: var(--content-w);
            padding-top: 0.5rem;
            padding-bottom: 4rem;
        }

        ::selection { background: var(--crimson-soft); color: #fff; }

        a:focus-visible, button:focus-visible, input:focus-visible,
        [tabindex]:focus-visible {
            outline: 2px solid var(--crimson-strong) !important;
            outline-offset: 2px !important;
        }

        @media (prefers-reduced-motion: reduce) {
            * { transition: none !important; animation: none !important; }
        }

        h1, h2, h3 { color: var(--ink) !important; font-family: var(--font-display); font-weight: 700 !important; letter-spacing: -0.01em; }
        label, .stMarkdown, p { color: var(--ink); font-weight: 500; }
        .stCaption, [data-testid="stCaptionContainer"] { color: var(--ink-faint) !important; font-size: 0.82rem !important; font-weight: 500 !important; }

        [id] { scroll-margin-top: 96px; }

        /* =====================================================
           NAVBAR — full-bleed, sticky
           ===================================================== */
        .ca-navbar {
            position: sticky;
            top: 0;
            z-index: 999;
            width: 100vw;
            margin-left: calc(50% - 50vw);
            background: rgba(9, 11, 16, 0.82);
            backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border);
        }

        .ca-navbar-inner {
            max-width: var(--content-w);
            margin: 0 auto;
            padding: 0 2rem;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .ca-nav-brand { display: flex; align-items: center; gap: 0.6rem; }

        .ca-nav-logo {
            width: 32px; height: 32px; border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            font-family: var(--font-display); font-weight: 800; font-size: 0.85rem; color: #fff;
            background: radial-gradient(circle at 30% 25%, var(--crimson-strong), #7a0e1f 100%);
        }

        .ca-nav-word { font-family: var(--font-display); font-weight: 800; font-size: 1.08rem; color: var(--ink); }

        .ca-nav-links { display: flex; align-items: center; gap: 1.8rem; }

        .ca-nav-links a {
            color: var(--ink-muted); text-decoration: none; font-size: 0.88rem; font-weight: 700;
            transition: color 0.15s ease;
        }
        .ca-nav-links a:hover { color: var(--ink); }

        .ca-nav-tag {
            font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: var(--ink-faint);
            border: 1px solid var(--border); border-radius: 100px; padding: 0.25rem 0.65rem;
        }

        /* =====================================================
           HERO
           ===================================================== */
        .ca-hero { text-align: center; padding: 3.6rem 1rem 2.4rem 1rem; }

        .ca-badge {
            display: inline-flex; align-items: center; gap: 0.4rem;
            font-family: var(--font-mono); font-size: 0.76rem; font-weight: 600; color: var(--ink-muted);
            border: 1px solid var(--border); border-radius: 100px;
            padding: 0.4rem 0.95rem; margin-bottom: 1.6rem;
            background: var(--panel);
        }

        .ca-hero h1 {
            font-family: var(--font-display) !important;
            font-weight: 900 !important;
            font-size: clamp(2.4rem, 5vw, 3.6rem) !important;
            line-height: 1.08 !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 1.2rem !important;
        }

        .ca-grad {
            background: var(--grad);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }

        .ca-hero-sub {
            max-width: 620px; margin: 0 auto 2rem auto;
            font-size: 1.08rem; line-height: 1.6; font-weight: 500; color: var(--ink-muted);
        }

        .ca-cta {
            display: inline-flex; align-items: center; gap: 0.5rem;
            background: linear-gradient(100deg, var(--crimson-strong), #b21a30);
            color: #fff !important; text-decoration: none;
            font-weight: 700; font-size: 0.98rem;
            padding: 0.85rem 1.7rem; border-radius: var(--radius-sm);
            box-shadow: 0 10px 30px -12px rgba(224, 38, 63, 0.55);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .ca-cta:hover { transform: translateY(-1px); box-shadow: 0 14px 34px -12px rgba(224, 38, 63, 0.7); }

        .ca-hero-note { margin-top: 0.9rem; font-size: 0.82rem; font-weight: 500; color: var(--ink-faint); }

        /* =====================================================
           CARDS (native st.container(border=True))
           ===================================================== */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--panel) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-lg) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius: var(--radius-lg); }

        .ca-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.9rem; }
        .ca-card-title { font-family: var(--font-display); font-weight: 800; font-size: 1.12rem; color: var(--ink); }
        .ca-card-eyebrow {
            font-family: var(--font-mono); font-size: 0.68rem; font-weight: 600; letter-spacing: 0.12em;
            text-transform: uppercase; color: var(--ink-faint); margin-bottom: 0.15rem;
        }

        .ca-status-pill {
            display: inline-flex; align-items: center; gap: 0.4rem;
            font-family: var(--font-mono); font-size: 0.75rem; font-weight: 600;
            padding: 0.3rem 0.7rem; border-radius: 100px; border: 1px solid var(--border);
        }
        .ca-status-dot { width: 7px; height: 7px; border-radius: 50%; }
        .ca-status-ready { color: var(--success); border-color: var(--success-soft); background: var(--success-soft); }
        .ca-status-ready .ca-status-dot { background: var(--success); }
        .ca-status-idle { color: var(--ink-faint); }
        .ca-status-idle .ca-status-dot { background: var(--ink-faint); }
        .ca-status-error { color: var(--crimson-strong); border-color: var(--crimson-soft); background: var(--crimson-soft); }
        .ca-status-error .ca-status-dot { background: var(--crimson-strong); }

        /* =====================================================
           TEXT INPUT
           ===================================================== */
        div[data-testid="stTextInput"] input {
            background: var(--panel-strong) !important;
            color: #fff !important;
            border: 1.5px solid var(--border-strong) !important;
            border-radius: var(--radius-md) !important;
            min-height: 50px !important;
            padding: 0 16px !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            transition: border-color 0.15s ease;
        }
        div[data-testid="stTextInput"] input:focus { border-color: var(--crimson) !important; }
        div[data-testid="stTextInput"] input::placeholder { color: var(--ink-faint) !important; }

        /* =====================================================
           FILE UPLOADER
           ===================================================== */
        div[data-testid="stFileUploader"] { background: transparent !important; border: none !important; padding: 0 !important; }
        div[data-testid="stFileUploaderDropzone"] {
            background: var(--panel-strong) !important;
            border: 1px dashed var(--border-strong) !important;
            border-radius: var(--radius-md) !important;
        }
        div[data-testid="stFileUploaderDropzone"] button {
            background: #171b26 !important; color: #fff !important;
            border: 1px solid var(--border-strong) !important; border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
        }

        /* =====================================================
           BUTTONS
           ===================================================== */
        .stButton > button {
            background: var(--panel-strong) !important;
            color: var(--ink) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            padding: 0.5rem 0.9rem !important;
            transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
        }
        .stButton > button:hover {
            border-color: var(--crimson) !important; color: #fff !important; background: var(--crimson-soft) !important;
        }

        /* =====================================================
           EXPANDERS
           ===================================================== */
        div[data-testid="stExpander"] {
            background: var(--panel) !important; border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
        }
        div[data-testid="stExpander"] summary { color: #f4f5f7 !important; font-weight: 700 !important; }

        /* =====================================================
           ALERTS
           ===================================================== */
        div[data-testid="stAlert"] { border-radius: var(--radius-md) !important; font-size: 0.9rem; font-weight: 500; }

        /* =====================================================
           EMPTY STATES
           ===================================================== */
        .ca-empty-state {
            font-size: 0.85rem; font-weight: 500; color: var(--ink-faint);
            border: 1px dashed var(--border); border-radius: var(--radius-md);
            padding: 0.85rem 1rem;
        }
        .ca-empty-state-lg { font-size: 0.95rem; font-weight: 500; color: var(--ink-muted); padding: 2.6rem 1rem; text-align: center; }

        /* =====================================================
           DOCUMENT CHIPS
           ===================================================== */
        .ca-doc-item {
            background: var(--panel-strong); border: 1px solid var(--border);
            border-radius: var(--radius-sm); padding: 0.5rem 0.75rem; margin-bottom: 0.5rem;
        }
        .ca-doc-name {
            font-size: 0.84rem; color: var(--ink); font-weight: 700;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }
        .ca-doc-badge { font-family: var(--font-mono); font-size: 0.7rem; font-weight: 600; color: var(--gold); margin-top: 0.15rem; }

        /* =====================================================
           ANSWER CARD
           ===================================================== */
        .ca-answer-body { font-size: 1.02rem; font-weight: 500; line-height: 1.65; color: var(--ink); white-space: pre-line; }
        .ca-source-pill { display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.7rem; }
        .ca-source-name { font-weight: 800; font-size: 0.85rem; color: var(--ink); }
        .ca-source-score { font-family: var(--font-mono); font-size: 0.72rem; font-weight: 600; color: var(--ink-faint); }

        /* =====================================================
           RECENT LIST
           ===================================================== */
        .ca-list-row { display: flex; align-items: center; gap: 0.9rem; padding: 0.85rem 0.2rem; border-bottom: 1px solid var(--border); }
        .ca-list-row:last-child { border-bottom: none; }
        .ca-list-icon {
            flex-shrink: 0; width: 34px; height: 34px; border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
            background: var(--panel-strong); border: 1px solid var(--border); font-size: 0.95rem;
        }
        .ca-list-title { font-size: 0.9rem; font-weight: 800; color: var(--ink); }
        .ca-list-sub { font-size: 0.78rem; font-weight: 500; color: var(--ink-faint); margin-top: 0.1rem; }
        .ca-list-time { margin-left: auto; font-size: 0.78rem; font-weight: 600; color: var(--ink-faint); flex-shrink: 0; }

        /* =====================================================
           FEATURE GRID
           ===================================================== */
        .ca-feature-icon {
            width: 40px; height: 40px; border-radius: 11px;
            display: flex; align-items: center; justify-content: center;
            background: var(--crimson-soft); font-size: 1.1rem; margin-bottom: 0.9rem;
        }
        .ca-feature-title { font-weight: 700; font-size: 1rem; color: var(--ink); margin-bottom: 0.35rem; }
        .ca-feature-desc { font-size: 0.85rem; font-weight: 500; line-height: 1.55; color: var(--ink-muted); }

        .ca-section-title {
            font-family: var(--font-display); font-weight: 800; font-size: 1.6rem;
            text-align: center; margin: 1rem 0 2rem 0;
        }

        /* =====================================================
           DEV PANEL METRICS
           ===================================================== */
        .ca-metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9rem; margin: 0.4rem 0 1rem 0; }
        .ca-metric { background: var(--panel-strong); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.9rem 1rem; text-align: center; }
        .ca-metric-value { font-family: var(--font-mono); font-size: 1.3rem; font-weight: 700; color: var(--ink); }
        .ca-metric-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); margin-top: 0.2rem; }

        /* =====================================================
           FOOTER
           ===================================================== */
        .ca-footer {
            margin-top: 3.5rem; padding-top: 2.2rem; border-top: 1px solid var(--border);
            display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem;
        }
        .ca-footer-tagline { font-size: 0.85rem; font-weight: 500; color: var(--ink-faint); margin-top: 0.4rem; max-width: 340px; }
        .ca-footer-copy { font-size: 0.78rem; font-weight: 500; color: var(--ink-faint); margin-top: 2rem; }

        div[data-testid="column"] > div { padding-top: 0 !important; }

        /* =====================================================
           RESPONSIVE
           ===================================================== */
        @media (max-width: 900px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .ca-navbar-inner { padding: 0 1rem; }
            .ca-nav-links { display: none; }
            .ca-metric-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )