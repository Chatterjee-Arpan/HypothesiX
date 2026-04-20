import streamlit as st


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0c111b;
            --bg-soft: #111827;
            --panel: rgba(17, 24, 39, 0.85);
            --panel-strong: rgba(22, 31, 49, 0.96);
            --line: rgba(148, 163, 184, 0.18);
            --text: #f8fafc;
            --muted: #94a3b8;
            --cyan: #67e8f9;
            --emerald: #34d399;
            --amber: #fbbf24;
            --rose: #fb7185;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(103, 232, 249, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(251, 191, 36, 0.1), transparent 26%),
                linear-gradient(180deg, #09101b 0%, #0c111b 48%, #090d14 100%);
            color: var(--text);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1600px;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
        }
        h1, h2, h3 {
            color: var(--text);
            letter-spacing: -0.02em;
        }
        p, label, .stMarkdown, .stCaption {
            color: var(--text);
        }
        .hero-shell, .section-shell, .result-card, .export-card, .pipeline-shell, .mermaid-shell {
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.72));
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
        }
        .hero-shell {
            padding: 1.4rem 1.5rem;
            margin-bottom: 1rem;
        }
        .hero-brand {
            color: var(--cyan);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: none;
            margin-bottom: 0.35rem;
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .hero-subtitle {
            color: var(--muted);
            font-size: 1rem;
            max-width: 760px;
        }
        .badge-row {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.82rem;
            color: var(--text);
            background: rgba(255,255,255,0.04);
        }
        .status-badge.merged { background: rgba(52, 211, 153, 0.12); color: #d1fae5; }
        .status-badge.conflict { background: rgba(251, 113, 133, 0.12); color: #ffe4e6; }
        .status-badge.gap { background: rgba(251, 191, 36, 0.14); color: #fef3c7; }
        .status-badge.unresolved { background: rgba(103, 232, 249, 0.1); color: #cffafe; }
        .status-badge.risky { background: rgba(248, 113, 113, 0.12); color: #fee2e2; }
        .status-badge.stable { background: rgba(52, 211, 153, 0.12); color: #d1fae5; }
        .section-shell, .pipeline-shell, .export-card {
            padding: 1rem 1.1rem;
            margin: 1rem 0;
        }
        .section-kicker {
            color: var(--cyan);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }
        .section-title {
            font-size: 1.55rem;
            font-weight: 650;
            margin: 0.15rem 0;
        }
        .section-note {
            color: var(--muted);
            font-size: 0.95rem;
        }
        .arena-shell {
            border-color: rgba(251, 113, 133, 0.25);
            background: linear-gradient(180deg, rgba(27, 14, 22, 0.96), rgba(22, 12, 20, 0.78));
        }
        .result-card {
            padding: 1rem 1rem 0.75rem 1rem;
            height: 100%;
        }
        .result-title {
            font-size: 0.82rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 0.65rem;
        }
        .result-value {
            font-size: 1rem;
            line-height: 1.6;
        }
        .list-chip {
            margin: 0 0 0.55rem 0;
            padding: 0.7rem 0.8rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
        }
        .panel-topline {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.65rem;
        }
        .result-card-wide {
            margin-bottom: 1rem;
        }
        .keyword-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 0.35rem;
        }
        .keyword-chip {
            display: inline-flex;
            align-items: center;
            padding: 0.55rem 0.9rem;
            border-radius: 999px;
            border: 1px solid rgba(103, 232, 249, 0.22);
            background: rgba(103, 232, 249, 0.08);
            color: #cffafe;
            font-size: 0.88rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .bullet-list {
            margin: 0.3rem 0 0 0;
            padding-left: 1.1rem;
        }
        .bullet-list li {
            color: var(--text);
            line-height: 1.6;
            margin-bottom: 0.65rem;
        }
        .bullet-list li::marker {
            color: var(--muted);
        }
        .tone-card {
            min-height: 100%;
        }
        .conflict-tone {
            background: linear-gradient(
                180deg,
                rgba(52, 24, 35, 0.92),
                rgba(24, 14, 20, 0.82)
            );
            border-color: rgba(251, 113, 133, 0.18);
        }
        .gap-tone {
            background: linear-gradient(
                180deg,
                rgba(48, 22, 54, 0.92),
                rgba(22, 14, 30, 0.82)
            );
            border-color: rgba(217, 70, 239, 0.18);
        }
        .risk-tone {
            background: linear-gradient(
                180deg,
                rgba(51, 36, 14, 0.92),
                rgba(24, 18, 10, 0.82)
            );
            border-color: rgba(251, 191, 36, 0.2);
        }
        .gladiator-row-gap {
            height: 1rem;
        }
        .gladiator-verdict-tone {
            background: linear-gradient(
                180deg,
                rgba(20, 34, 70, 0.94),
                rgba(14, 24, 48, 0.84)
            );
            border-color: rgba(103, 232, 249, 0.18);
        }
        .gladiator-confidence-tone {
            background: linear-gradient(
                180deg,
                rgba(24, 31, 56, 0.94),
                rgba(16, 22, 40, 0.84)
            );
            border-color: rgba(148, 163, 184, 0.18);
        }
        .gladiator-attack-tone {
            background: linear-gradient(
                180deg,
                rgba(55, 24, 32, 0.94),
                rgba(26, 14, 18, 0.84)
            );
            border-color: rgba(251, 113, 133, 0.18);
        }
        .gladiator-assumption-tone {
            background: linear-gradient(
                180deg,
                rgba(62, 38, 16, 0.94),
                rgba(28, 18, 10, 0.84)
            );
            border-color: rgba(251, 191, 36, 0.2);
        }
        .gladiator-claims-tone {
            background: linear-gradient(
                180deg,
                rgba(45, 24, 58, 0.94),
                rgba(21, 13, 28, 0.84)
            );
            border-color: rgba(217, 70, 239, 0.18);
        }
        .gladiator-execution-tone {
            background: linear-gradient(
                180deg,
                rgba(47, 24, 16, 0.94),
                rgba(23, 13, 10, 0.84)
            );
            border-color: rgba(251, 146, 60, 0.2);
        }
        .gladiator-adoption-tone {
            background: linear-gradient(
                180deg,
                rgba(22, 46, 35, 0.94),
                rgba(12, 22, 18, 0.84)
            );
            border-color: rgba(52, 211, 153, 0.18);
        }
        .gladiator-scope-tone {
            background: linear-gradient(
                180deg,
                rgba(51, 23, 36, 0.94),
                rgba(23, 12, 18, 0.84)
            );
            border-color: rgba(244, 114, 182, 0.18);
        }
        .gladiator-danger-tone {
            background: linear-gradient(
                180deg,
                rgba(60, 24, 24, 0.94),
                rgba(26, 12, 12, 0.84)
            );
            border-color: rgba(248, 113, 113, 0.22);
        }
        .gladiator-step-tone {
            background: linear-gradient(
                180deg,
                rgba(18, 44, 58, 0.94),
                rgba(10, 20, 28, 0.84)
            );
            border-color: rgba(34, 211, 238, 0.18);
        }
        .gladiator-toprisks-tone {
            background: linear-gradient(
                180deg,
                rgba(58, 40, 12, 0.94),
                rgba(25, 18, 8, 0.84)
            );
            border-color: rgba(251, 191, 36, 0.22);
        }
        .conflict-panel-note {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.5;
            padding: 0.2rem 0 0.7rem 0;
        }
        .conflict-resolution-card {
            margin-top: 0.85rem;
            padding: 0.95rem 1rem 0.8rem 1rem;
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: linear-gradient(
                180deg,
                rgba(17, 24, 39, 0.9),
                rgba(15, 23, 42, 0.76)
            );
        }
        .conflict-card-label {
            color: var(--text);
            font-size: 1rem;
            line-height: 1.5;
        }
        .history-entry {
            margin-bottom: 0.6rem;
            padding: 0.75rem 0.85rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            color: var(--text);
            line-height: 1.5;
        }
        .pipeline-step {
            padding: 0.85rem 1rem;
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.06);
            background: rgba(255,255,255,0.03);
            margin-bottom: 0.55rem;
            transition: all 180ms ease-in-out;
        }
        .pipeline-step.running {
            border-color: rgba(103, 232, 249, 0.34);
            background: rgba(103, 232, 249, 0.08);
        }
        .pipeline-step.completed {
            border-color: rgba(52, 211, 153, 0.3);
            background: rgba(52, 211, 153, 0.08);
        }
        .pipeline-step.pending {
            color: var(--muted);
        }
        .pipeline-step-compact {
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 0;
        }
        .pipeline-step-compact {
            min-height: 112px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 0;
        }
        .mermaid-shell {
            padding: 1rem;
            margin-top: 1rem;
        }
        .mermaid {
            background: rgba(255,255,255,0.02);
            border-radius: 18px;
            padding: 1rem;
        }
        .stTextArea textarea,
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            background: rgba(0, 0, 0, 0.92) !important;
            color: #ffffff !important;
            border: 1px solid rgba(148, 163, 184, 0.28) !important;
            border-radius: 16px !important;
            caret-color: #ffffff !important;
        }
        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {
            color: #94a3b8 !important;
            opacity: 1 !important;
        }
        .stSelectbox div[data-baseweb="select"] span,
        .stSelectbox div[data-baseweb="select"] input {
            color: #ffffff !important;
        }
        .stTextArea textarea:focus,
        .stTextInput input:focus,
        .stSelectbox div[data-baseweb="select"] > div:focus-within {
            border-color: rgba(103, 232, 249, 0.45) !important;
            box-shadow: 0 0 0 1px rgba(103, 232, 249, 0.18) !important;
        }
        .stButton > button {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96)) !important;
            color: var(--text) !important;
            border: 1px solid rgba(103, 232, 249, 0.22) !important;
            border-radius: 14px !important;
            min-height: 2.8rem !important;
            font-weight: 600 !important;
            transition: all 160ms ease-in-out;
        }
        .stButton > button:hover {
            border-color: rgba(103, 232, 249, 0.45) !important;
            box-shadow: 0 0 0 1px rgba(103, 232, 249, 0.18) !important;
            color: var(--text) !important;
        }
        .stButton > button:disabled {
            background: rgba(148, 163, 184, 0.12) !important;
            color: #cbd5e1 !important;
            border-color: rgba(148, 163, 184, 0.18) !important;
            cursor: not-allowed !important;
            opacity: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
