import io
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf


st.set_page_config(page_title="Stock Insight Neon", page_icon="📈", layout="wide")


st.markdown(
    """
<style>
:root {
    --neon-cyan:#22d3ee;
    --neon-blue:#38bdf8;
    --neon-purple:#a855f7;
    --neon-pink:#f472b6;
    --neon-red:#fb365c;
    --ink:#020617;
    --panel:rgba(8,13,28,.82);
    --panel-strong:rgba(7,11,24,.94);
    --muted:#94a3b8;
}

.stApp {
    background:
        radial-gradient(circle at 12% 6%, rgba(168,85,247,.28), transparent 28%),
        radial-gradient(circle at 86% 2%, rgba(34,211,238,.22), transparent 24%),
        radial-gradient(circle at 68% 72%, rgba(244,63,94,.12), transparent 32%),
        linear-gradient(135deg,#01030a 0%,#020617 44%,#0b1022 72%,#14071d 100%);
    color:#e5e7eb;
    overflow-x:hidden;
}

.stApp::before {
    content:"";
    position:fixed;
    inset:0;
    z-index:0;
    pointer-events:none;
    opacity:.28;
    background:
        repeating-linear-gradient(180deg, rgba(255,255,255,.045) 0 1px, transparent 1px 4px),
        linear-gradient(90deg, transparent 0%, rgba(34,211,238,.08) 48%, transparent 50%, rgba(168,85,247,.06) 52%, transparent 100%);
    mix-blend-mode:screen;
}

.stApp::after {
    content:"";
    position:fixed;
    inset:-20% 0 0 0;
    z-index:0;
    pointer-events:none;
    opacity:.16;
    background-image:
        linear-gradient(115deg, transparent 0 46%, rgba(34,211,238,.45) 47%, transparent 48%),
        linear-gradient(112deg, transparent 0 62%, rgba(148,163,184,.45) 63%, transparent 64%),
        linear-gradient(118deg, transparent 0 76%, rgba(244,114,182,.36) 77%, transparent 78%);
    background-size: 420px 100%, 560px 100%, 720px 100%;
    animation: neonRain 9s linear infinite;
}

@keyframes neonRain {
    from { transform:translate3d(0,-10%,0); }
    to { transform:translate3d(-7%,22%,0); }
}

.block-container {
    position:relative;
    z-index:1;
    padding-top:2rem;
    padding-bottom:3rem;
    max-width:1280px;
}

section[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(1,3,10,.98), rgba(8,13,28,.96), rgba(31,13,54,.94)),
        repeating-linear-gradient(180deg, transparent 0 9px, rgba(34,211,238,.06) 10px 11px);
    border-right:1px solid rgba(34,211,238,.36);
    box-shadow: 12px 0 42px rgba(34,211,238,.08);
}

section[data-testid="stSidebar"] * { color:#f8fafc !important; }
section[data-testid="stSidebar"] .stCaption { color:#cbd5e1 !important; }

h1,h2,h3 {
    color:#f8fafc !important;
    letter-spacing:.02em;
    text-shadow:0 0 18px rgba(34,211,238,.35), 0 0 32px rgba(168,85,247,.18);
}

a { color:#67e8f9 !important; }

.neon-title {
    font-size:46px;
    line-height:1;
    font-weight:950;
    letter-spacing:.04em;
    text-transform:uppercase;
    background:linear-gradient(90deg,#22d3ee,#60a5fa,#a855f7,#f472b6);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    filter:drop-shadow(0 0 18px rgba(34,211,238,.55));
}

.neon-subtitle {
    color:#bae6fd;
    font-family:"Courier New", monospace;
    letter-spacing:.18em;
    text-transform:uppercase;
    margin-top:.4rem;
    text-shadow:0 0 14px rgba(34,211,238,.48);
}

.terminal-line {
    font-family:"Courier New", monospace;
    color:#7dd3fc;
    border-left:3px solid rgba(34,211,238,.7);
    padding:8px 12px;
    background:linear-gradient(90deg, rgba(34,211,238,.10), transparent);
    margin:8px 0 18px;
}

.card {
    position:relative;
    background:
        linear-gradient(180deg, rgba(15,23,42,.86), rgba(2,6,23,.82)),
        radial-gradient(circle at 100% 0%, rgba(34,211,238,.14), transparent 30%);
    border:1px solid rgba(34,211,238,.27);
    border-radius:22px;
    padding:22px;
    box-shadow:0 0 35px rgba(34,211,238,.12), inset 0 0 32px rgba(168,85,247,.04);
    backdrop-filter:blur(14px);
    margin-bottom:18px;
}

.card::before {
    content:"";
    position:absolute;
    inset:0;
    border-radius:22px;
    pointer-events:none;
    border-top:1px solid rgba(255,255,255,.08);
}

.kpi {
    background:
        linear-gradient(180deg, rgba(15,23,42,.88), rgba(3,7,18,.88)),
        radial-gradient(circle at 80% 0%, rgba(168,85,247,.22), transparent 44%);
    border:1px solid rgba(168,85,247,.38);
    border-radius:18px;
    padding:18px;
    min-height:116px;
    box-shadow:0 0 24px rgba(168,85,247,.18), inset 0 0 24px rgba(34,211,238,.04);
}

.kpi-title {
    color:#94a3b8;
    font-size:12px;
    text-transform:uppercase;
    font-weight:900;
    letter-spacing:.12em;
    font-family:"Courier New", monospace;
}

.kpi-value {
    font-size:26px;
    font-weight:950;
    color:#f8fafc;
    margin-top:8px;
    text-shadow:0 0 18px rgba(34,211,238,.35);
}

.kpi-good { color:#67e8f9 !important; }
.kpi-bad { color:#fb7185 !important; }

.notice, .data-missing, .mini-chip {
    border-radius:16px;
    padding:14px 18px;
    margin-bottom:18px;
    font-family:"Courier New", monospace;
}

.notice {
    background:rgba(16,185,129,.10);
    border:1px solid rgba(34,211,238,.45);
    color:#bbf7d0;
    box-shadow:0 0 18px rgba(34,211,238,.08);
}

.data-missing {
    background:rgba(251,54,92,.10);
    border:1px solid rgba(244,114,182,.32);
    color:#fecdd3;
    box-shadow:0 0 20px rgba(244,63,94,.10);
}

.mini-chip {
    display:inline-block;
    margin:4px 6px 8px 0;
    padding:7px 11px;
    background:rgba(15,23,42,.78);
    border:1px solid rgba(34,211,238,.26);
    color:#cffafe;
    font-size:12px;
}

div.stButton > button,
button[kind="primary"],
button[kind="secondary"] {
    background:linear-gradient(135deg,#06b6d4,#2563eb,#8b5cf6,#ec4899)!important;
    color:white!important;
    border:1px solid rgba(255,255,255,.18)!important;
    border-radius:14px!important;
    font-weight:950!important;
    letter-spacing:.03em!important;
    box-shadow:0 0 22px rgba(168,85,247,.45), inset 0 0 18px rgba(255,255,255,.08)!important;
    transition:transform .12s ease, filter .12s ease, box-shadow .12s ease!important;
}

div.stButton > button:hover {
    transform:translateY(-1px);
    filter:saturate(1.18) brightness(1.12);
    box-shadow:0 0 30px rgba(34,211,238,.55), 0 0 46px rgba(236,72,153,.22)!important;
}

.stTabs [data-baseweb="tab-list"] {
    gap:10px;
    border-bottom:1px solid rgba(34,211,238,.18);
}

.stTabs [data-baseweb="tab"] {
    background:rgba(15,23,42,.72);
    border:1px solid rgba(34,211,238,.20);
    border-radius:12px 12px 0 0;
    color:#e5e7eb;
    box-shadow:0 0 12px rgba(34,211,238,.06);
}

.stTabs [aria-selected="true"] {
    color:#ffffff !important;
    border-color:rgba(34,211,238,.65) !important;
    box-shadow:0 0 18px rgba(34,211,238,.22), inset 0 0 18px rgba(34,211,238,.10);
}

input, textarea {
    background: rgba(3,7,18,.96) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(34,211,238,.58) !important;
    border-radius: 14px !important;
    box-shadow: inset 0 0 18px rgba(34,211,238,.06), 0 0 14px rgba(34,211,238,.08) !important;
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
}

div[data-baseweb="select"] * {
    background-color: rgba(3,7,18,.96) !important;
    color: #f8fafc !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label {
    color: #e5e7eb !important;
    font-weight:800 !important;
}

div[data-testid="stMetric"] {
    background:rgba(8,13,28,.78);
    border:1px solid rgba(34,211,238,.22);
    border-radius:18px;
    padding:18px;
    box-shadow:0 0 20px rgba(34,211,238,.08);
}

div[data-testid="stMetric"] label { color:#bae6fd !important; }
div[data-testid="stMetricValue"] { color:#f8fafc !important; }

.stDataFrame, div[data-testid="stTable"] {
    border:1px solid rgba(34,211,238,.22);
    border-radius:16px;
    overflow:hidden;
}

hr {
    border-color:rgba(34,211,238,.18) !important;
}

.footer {
    color:#94a3b8;
    font-size:12px;
    font-family:"Courier New", monospace;
    text-align:center;
    margin-top:24px;
}
</style>
""",
    unsafe_allow_html=True,
)


components.html(
    """
<script>
(function () {
  const STATE = {
    ctx: null,
    bound: new WeakSet(),
    started: false
  };

  function getDoc() {
    try {
      if (window.parent && window.parent.document) return window.parent.document;
    } catch (e) {}
    return document;
  }

  function ensureAudio() {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return null;
    if (!STATE.ctx) {
      STATE.ctx = new AudioContext();
    }
    if (STATE.ctx.state === "suspended") {
      STATE.ctx.resume().catch(function () {});
    }
    STATE.started = true;
    return STATE.ctx;
  }

  function tone(freq, start, duration, type, gainValue) {
    const ctx = ensureAudio();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    osc.type = type || "triangle";
    osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
    filter.type = "highpass";
    filter.frequency.setValueAtTime(320, ctx.currentTime + start);
    gain.gain.setValueAtTime(0.0001, ctx.currentTime + start);
    gain.gain.exponentialRampToValueAtTime(gainValue || 0.055, ctx.currentTime + start + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + start + duration);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime + start);
    osc.stop(ctx.currentTime + start + duration + 0.02);
  }

  function neonClick() {
    tone(820, 0.00, 0.055, "square", 0.030);
    tone(1240, 0.035, 0.060, "triangle", 0.022);
  }

  function scanSound() {
    const ctx = ensureAudio();
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    osc.type = "sawtooth";
    filter.type = "bandpass";
    filter.Q.value = 9;
    osc.frequency.setValueAtTime(190, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1420, ctx.currentTime + 0.34);
    filter.frequency.setValueAtTime(420, ctx.currentTime);
    filter.frequency.exponentialRampToValueAtTime(2200, ctx.currentTime + 0.34);
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.045, ctx.currentTime + 0.025);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.38);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.42);
  }

  function addSound() {
    tone(520, 0.00, 0.075, "sine", 0.026);
    tone(780, 0.060, 0.090, "triangle", 0.024);
    tone(1040, 0.125, 0.085, "sine", 0.018);
  }

  function bindSounds() {
    const doc = getDoc();
    const nodes = doc.querySelectorAll("button, [role='tab'], input");
    nodes.forEach(function (node) {
      if (STATE.bound.has(node)) return;
      STATE.bound.add(node);
      node.addEventListener("click", function () {
        const text = (node.innerText || node.value || node.getAttribute("aria-label") || "").toLowerCase();
        if (text.includes("scanner")) {
          scanSound();
        } else if (text.includes("watchlist") || text.includes("ajouter")) {
          addSound();
        } else if (node.getAttribute("role") === "tab") {
          neonClick();
        } else if (text.includes("recherche") || text.includes("lancer")) {
          neonClick();
        } else if (node.tagName === "BUTTON") {
          neonClick();
        }
      }, { passive: true });

      node.addEventListener("change", function () {
        if (node.tagName === "INPUT") neonClick();
      }, { passive: true });
    });
  }

  bindSounds();
  setInterval(bindSounds, 900);
})();
</script>
""",
    height=0,
)


BASE_ASSETS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Meta": "META",
    "Google": "GOOGL",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Intel": "INTC",
    "Palantir": "PLTR",
    "Coinbase": "COIN",
    "Berkshire Hathaway": "BRK-B",
    "Visa": "V",
    "Mastercard": "MA",
    "JPMorgan": "JPM",
    "BlackRock": "BLK",
    "McDonald's": "MCD",
    "Coca-Cola": "KO",
    "Pepsi": "PEP",
    "Nike": "NKE",
    "Walmart": "WMT",
    "Costco": "COST",
    "Eli Lilly": "LLY",
    "Broadcom": "AVGO",
    "Oracle": "ORCL",
    "Salesforce": "CRM",
    "Adobe": "ADBE",
    "Cisco": "CSCO",
    "Qualcomm": "QCOM",
    "Texas Instruments": "TXN",
    "Uber": "UBER",
    "Shopify": "SHOP",
    "Sea Limited": "SE",
    "MercadoLibre": "MELI",
    "LVMH": "MC.PA",
    "TotalEnergies": "TTE.PA",
    "Airbus": "AIR.PA",
    "BNP Paribas": "BNP.PA",
    "Schneider Electric": "SU.PA",
    "Hermes": "RMS.PA",
    "Safran": "SAF.PA",
    "Sanofi": "SAN.PA",
    "AXA": "CS.PA",
    "Dassault Systemes": "DSY.PA",
    "L'Oreal": "OR.PA",
    "Kering": "KER.PA",
    "Renault": "RNO.PA",
    "Stellantis": "STLAP.PA",
    "Societe Generale": "GLE.PA",
    "Credit Agricole": "ACA.PA",
    "CAC 40": "^FCHI",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "Euro Stoxx 50": "^STOXX50E",
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD",
    "Avalanche": "AVAX-USD",
    "Chainlink": "LINK-USD",
    "Polkadot": "DOT-USD",
    "Polygon": "MATIC-USD",
    "Litecoin": "LTC-USD",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Copper": "HG=F",
    "Oil WTI": "CL=F",
    "Brent Oil": "BZ=F",
    "Natural Gas": "NG=F",
    "Corn": "ZC=F",
    "Soybean": "ZS=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "CAD=X",
    "SPY ETF": "SPY",
    "QQQ ETF": "QQQ",
    "Vanguard S&P 500 ETF": "VOO",
    "iShares MSCI World ETF": "URTH",
    "ARK Innovation ETF": "ARKK",
    "iShares Russell 2000 ETF": "IWM",
    "Financial Select Sector ETF": "XLF",
    "Technology Select Sector ETF": "XLK",
    "Energy Select Sector ETF": "XLE",
    "Gold ETF": "GLD",
}


def safe_number(value, decimals=2, suffix=""):
    try:
        if value is None or pd.isna(value):
            return "N/D"
        number = float(value)
        return f"{number:.{decimals}f}{suffix}"
    except Exception:
        return "N/D"


def format_int(value):
    try:
        if value is None or pd.isna(value):
            return "N/D"
        return f"{int(float(value)):,}".replace(",", " ")
    except Exception:
        return "N/D"


@st.cache_data(ttl=86400, show_spinner=False)
def load_catalog():
    rows = []
    for name, symbol_value in BASE_ASSETS.items():
        rows.append({"name": name, "symbol": symbol_value, "type": "Catalogue"})

    sources = [
        (
            "NASDAQ",
            "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
            "Symbol",
            "Security Name",
        ),
        (
            "NYSE/AMEX",
            "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
            "ACT Symbol",
            "Security Name",
        ),
    ]

    for market_type, url, symbol_col, name_col in sources:
        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text), sep="|")
            if "Test Issue" in df.columns:
                df = df[df["Test Issue"] == "N"]
            for _, row in df.head(1500).iterrows():
                symbol_value = str(row.get(symbol_col, "")).replace(".", "-").strip()
                asset_name = str(row.get(name_col, "")).strip()
                if symbol_value and symbol_value.lower() != "nan" and asset_name:
                    rows.append({"name": asset_name, "symbol": symbol_value, "type": market_type})
        except Exception:
            continue

    catalog_df = pd.DataFrame(rows).dropna()
    catalog_df = catalog_df[catalog_df["symbol"].astype(str).str.len() > 0]
    catalog_df = catalog_df.drop_duplicates("symbol")
    catalog_df = catalog_df.sort_values(["type", "name"], kind="stable").reset_index(drop=True)
    return catalog_df


@st.cache_data(ttl=7200, show_spinner=False)
def get_history(symbol):
    try:
        data = yf.download(
            symbol,
            period="6mo",
            progress=False,
            threads=False,
            auto_adjust=False,
        )
        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        expected = ["Open", "High", "Low", "Close", "Volume"]
        for column in expected:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors="coerce")

        data = data.dropna(subset=["Close"])
        return data
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_info(symbol):
    try:
        info = yf.Ticker(symbol).info
        if isinstance(info, dict):
            return info
        return {}
    except Exception:
        return {}


def money(x):
    try:
        if x is None or pd.isna(x):
            return "N/D"
        x = float(x)
        if abs(x) >= 1_000_000_000_000:
            return f"${x/1_000_000_000_000:.2f}T"
        if abs(x) >= 1_000_000_000:
            return f"${x/1_000_000_000:.2f}B"
        if abs(x) >= 1_000_000:
            return f"${x/1_000_000:.2f}M"
        return f"${x:,.2f}"
    except Exception:
        return "N/D"


def tv_symbol(symbol):
    if symbol.endswith("-USD"):
        return "CRYPTO:" + symbol.replace("-USD", "USD")
    if symbol.endswith(".PA"):
        return "EURONEXT:" + symbol.replace(".PA", "")
    if symbol.startswith("^"):
        return symbol
    if symbol.endswith("=F") or symbol.endswith("=X"):
        return symbol
    return "NASDAQ:" + symbol


def unavailable_box(message="Données temporairement indisponibles"):
    st.markdown(
        f'<div class="data-missing">▣ {message}. Yahoo Finance peut limiter les requêtes. '
        "Réessaie dans quelques minutes ou sélectionne un autre actif.</div>",
        unsafe_allow_html=True,
    )


def kpi_card(title, value, tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f'<div class="kpi"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value{tone_class}">{value}</div></div>',
        unsafe_allow_html=True,
    )


def get_close_series(history):
    if history is None or history.empty or "Close" not in history.columns:
        return pd.Series(dtype="float64")
    close_data = history["Close"]
    if isinstance(close_data, pd.DataFrame):
        close_data = close_data.iloc[:, 0]
    return pd.to_numeric(close_data, errors="coerce").dropna()


def price_line(value, currency):
    try:
        return f"{float(value):,.2f} {currency}".replace(",", " ")
    except Exception:
        return "N/D"


catalog = load_catalog()

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

with st.sidebar:
    st.markdown('<div class="neon-title">Stock Insight</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Neon Terminal</div>', unsafe_allow_html=True)
    st.caption("Radar financier cyberpunk sans API payante")
    st.markdown("---")

    query = st.text_input("🔎 Recherche action / crypto / ETF / forex", "Apple")
    st.button("Lancer la recherche", key="launch_search")
    q = query.lower().strip()

    if q:
        filtered = catalog[
            catalog["name"].str.lower().str.contains(q, na=False)
            | catalog["symbol"].str.lower().str.contains(q, na=False)
        ].head(60)
    else:
        filtered = catalog.head(60)

    if filtered.empty:
        filtered = catalog.head(40)
        st.markdown(
            '<div class="data-missing">Aucun signal dans le catalogue pour cette recherche. '
            "Affichage des premiers actifs disponibles.</div>",
            unsafe_allow_html=True,
        )

    labels = filtered.apply(lambda r: f"{r['symbol']} — {r['name']} [{r['type']}]", axis=1).tolist()
    selected_label = st.selectbox("Palette de marché", labels)
    symbol = selected_label.split(" — ")[0].strip()

    scanner_clicked = st.button("⚡ Scanner l’actif", key="scan_asset")
    if scanner_clicked:
        st.toast(f"Scan néon lancé pour {symbol}", icon="⚡")

    st.markdown("---")
    st.caption(f"Catalogue chargé : {len(catalog)} actifs")
    st.caption("Historique cache : 2h · Catalogue : 24h")
    st.caption("Sons : activés après interaction utilisateur")


hist = get_history(symbol)
info = get_info(symbol)
close = get_close_series(hist)
data_available = not close.empty

name = info.get("longName") or info.get("shortName") or symbol
sector = info.get("sector", "N/D")
industry = info.get("industry", "N/D")
country = info.get("country", "N/D")
currency = info.get("currency", "USD")
price = float(close.iloc[-1]) if data_available else None
previous = float(close.iloc[-2]) if len(close) > 1 else price
change = ((price - previous) / previous) * 100 if price is not None and previous else None


st.markdown('<div class="neon-title">📈 Stock Insight Neon Terminal</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="terminal-line">MODE DETECTIVE FINANCIER · PLUIE SYNTHETIQUE · DONNEES PUBLIQUES · '
    f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="notice">⚠️ Analyse éducative générée depuis des données publiques. '
    "Aucun conseil financier. Aucun abonnement API obligatoire.</div>",
    unsafe_allow_html=True,
)

st.title(name)
st.caption(f"{symbol} · {sector} · {industry} · {country}")

if not data_available:
    unavailable_box()

tabs = st.tabs(
    [
        "🏠 Accueil",
        "🌍 Marché",
        "📈 Performance",
        "📊 Ratios",
        "⚠️ Risque",
        "🧠 Résumé",
        "🔥 Heatmap",
        "🌐 TradingView",
        "⭐ Watchlist",
    ]
)

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Prix", price_line(price, currency) if price is not None else "N/D")
    with c2:
        change_text = safe_number(change, 2, "%")
        change_tone = "kpi-good" if change is not None and change >= 0 else "kpi-bad"
        kpi_card("Variation jour", change_text, change_tone if change is not None else "")
    with c3:
        kpi_card("Market Cap", money(info.get("marketCap")))
    with c4:
        kpi_card("Beta", safe_number(info.get("beta"), 2))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏢 Fiche entreprise")
    st.write(f"**Nom :** {name}")
    st.write(f"**Symbole :** {symbol}")
    st.write(f"**Secteur :** {sector}")
    st.write(f"**Industrie :** {industry}")
    st.write(f"**Pays :** {country}")
    st.write(f"**Employés :** {format_int(info.get('fullTimeEmployees'))}")
    st.write(f"**Devise :** {currency}")
    if info.get("website"):
        st.markdown(f"[🌐 Site officiel]({info.get('website')})")
    if info.get("longBusinessSummary"):
        st.markdown("**Briefing nocturne :**")
        st.write(str(info.get("longBusinessSummary"))[:900] + "...")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("🌍 Marché")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Type :** {info.get('quoteType', 'N/D')}")
    st.write(f"**Devise :** {currency}")
    st.write(f"**Exchange :** {info.get('exchange', 'N/D')}")
    st.write(f"**Fuseau marché :** {info.get('exchangeTimezoneName', 'N/D')}")
    st.write(f"**Volume :** {format_int(info.get('volume'))}")
    st.write(f"**Volume moyen :** {format_int(info.get('averageVolume'))}")
    st.write(f"**Ouverture :** {price_line(info.get('open'), currency)}")
    st.write(f"**Plus haut jour :** {price_line(info.get('dayHigh'), currency)}")
    st.write(f"**Plus bas jour :** {price_line(info.get('dayLow'), currency)}")
    st.write(f"**52 semaines haut / bas :** {price_line(info.get('fiftyTwoWeekHigh'), currency)} / {price_line(info.get('fiftyTwoWeekLow'), currency)}")
    st.markdown("</div>", unsafe_allow_html=True)

    if data_available:
        market_df = pd.DataFrame(
            {
                "Signal": ["Dernier prix", "Variation jour", "Début période", "Fin période"],
                "Valeur": [
                    price_line(price, currency),
                    safe_number(change, 2, "%"),
                    price_line(close.iloc[0], currency),
                    price_line(close.iloc[-1], currency),
                ],
            }
        )
        st.dataframe(market_df, use_container_width=True, hide_index=True)
    else:
        unavailable_box("Données de marché temporairement indisponibles")

with tabs[2]:
    st.subheader("📈 Performance holographique")
    if data_available and {"Open", "High", "Low", "Close"}.issubset(hist.columns):
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                increasing_line_color="#22d3ee",
                decreasing_line_color="#fb365c",
                name="Prix",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=close.tail(90).index,
                y=close.tail(90).rolling(20).mean(),
                mode="lines",
                line=dict(color="#a855f7", width=2),
                name="Moyenne 20",
            )
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(2,6,23,.85)",
            height=560,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10),
            font=dict(color="#e5e7eb"),
        )
        fig.update_xaxes(gridcolor="rgba(34,211,238,.10)")
        fig.update_yaxes(gridcolor="rgba(34,211,238,.10)")
        st.plotly_chart(fig, use_container_width=True)

        perf = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100 if close.iloc[0] else 0
        st.markdown(
            f'<span class="mini-chip">Performance 6 mois : {perf:.2f}%</span>'
            f'<span class="mini-chip">Points historiques : {len(close)}</span>',
            unsafe_allow_html=True,
        )
    else:
        unavailable_box("Graphique temporairement indisponible")

with tabs[3]:
    st.subheader("📊 Ratios")
    r1, r2, r3 = st.columns(3)
    with r1:
        kpi_card("P/E", safe_number(info.get("trailingPE"), 2))
    with r2:
        kpi_card("Forward P/E", safe_number(info.get("forwardPE"), 2))
    with r3:
        dividend = info.get("dividendYield")
        dividend_text = safe_number(dividend * 100, 2, "%") if isinstance(dividend, (int, float)) else "N/D"
        kpi_card("Dividend Yield", dividend_text)

    r4, r5, r6 = st.columns(3)
    with r4:
        kpi_card("Price / Book", safe_number(info.get("priceToBook"), 2))
    with r5:
        kpi_card("Marge profit", safe_number((info.get("profitMargins") or 0) * 100, 2, "%") if info.get("profitMargins") is not None else "N/D")
    with r6:
        kpi_card("Dette / Equity", safe_number(info.get("debtToEquity"), 2))

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Chiffre d'affaires :** {money(info.get('totalRevenue'))}")
    st.write(f"**EBITDA :** {money(info.get('ebitda'))}")
    st.write(f"**Cash total :** {money(info.get('totalCash'))}")
    st.write(f"**Dette totale :** {money(info.get('totalDebt'))}")
    st.write(f"**Recommandation moyenne Yahoo :** {info.get('recommendationKey', 'N/D')}")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    st.subheader("⚠️ Risque")
    if data_available and len(close) >= 3:
        returns = close.pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5) * 100
        drawdown = ((close / close.cummax()) - 1).min() * 100
        downside = returns[returns < 0].std() * (252 ** 0.5) * 100 if not returns[returns < 0].empty else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Volatilité estimée", f"{volatility:.2f}%")
        c2.metric("Perte max période", f"{drawdown:.2f}%")
        c3.metric("Volatilité baissière", f"{downside:.2f}%")

        risk_level = "faible"
        if volatility >= 55 or drawdown <= -35:
            risk_level = "élevé"
        elif volatility >= 30 or drawdown <= -18:
            risk_level = "modéré"

        st.markdown(
            f'<div class="notice">Niveau de risque détecté : <strong>{risk_level}</strong>. '
            "Une forte volatilité signifie que le prix peut varier rapidement. Aucun rendement n'est garanti.</div>",
            unsafe_allow_html=True,
        )

        fig_risk = go.Figure()
        fig_risk.add_trace(
            go.Scatter(
                x=close.index,
                y=((close / close.cummax()) - 1) * 100,
                fill="tozeroy",
                mode="lines",
                line=dict(color="#fb365c"),
                name="Drawdown",
            )
        )
        fig_risk.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(2,6,23,.85)",
            height=360,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    else:
        unavailable_box("Module risque temporairement indisponible")

with tabs[5]:
    st.subheader("🧠 Résumé IA local")
    if data_available:
        ma20 = close.tail(20).mean()
        ma60 = close.tail(60).mean() if len(close) >= 60 else ma20
        perf = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100 if close.iloc[0] else 0
        volatility = close.pct_change().std() * (252 ** 0.5) * 100

        score = 0
        if price > ma20:
            score += 1
        if price > ma60:
            score += 1
        if perf > 5:
            score += 1
        if volatility < 35:
            score += 1

        if score >= 3:
            reco = "intéressant à surveiller, tendance constructive"
            reco_class = "kpi-good"
        elif score == 2:
            reco = "neutre, à surveiller avec prudence"
            reco_class = ""
        else:
            reco = "risqué ou faible momentum"
            reco_class = "kpi-bad"

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f"""
### Verdict éducatif : <span class="{reco_class}">**{reco}**</span>

- Prix actuel : **{price_line(price, currency)}**
- Moyenne 20 jours : **{price_line(ma20, currency)}**
- Moyenne 60 jours : **{price_line(ma60, currency)}**
- Performance 6 mois : **{perf:.2f}%**
- Volatilité estimée : **{volatility:.2f}%**
- Score terminal : **{score}/4**

⚠️ Ceci n'est pas un conseil financier. Risque de perte en capital.
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        unavailable_box("Résumé temporairement indisponible")

with tabs[6]:
    st.subheader("🔥 Heatmap néon")
    st.caption("Heatmap volontairement limitée pour réduire les risques de rate limit Yahoo Finance.")

    heatmap_symbols = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA",
        "AMZN",
        "META",
        "GOOGL",
        "BTC-USD",
    ]
    perf_rows = []

    for heat_symbol in heatmap_symbols:
        try:
            heat_hist = get_history(heat_symbol)
            heat_close = get_close_series(heat_hist)
            if len(heat_close) >= 2 and heat_close.iloc[0]:
                performance = ((heat_close.iloc[-1] - heat_close.iloc[0]) / heat_close.iloc[0]) * 100
                perf_rows.append({"symbol": heat_symbol, "performance": performance})
        except Exception:
            continue

    if perf_rows:
        dfp = pd.DataFrame(perf_rows)
        fig = px.treemap(
            dfp,
            path=["symbol"],
            values=dfp["performance"].abs() + 1,
            color="performance",
            color_continuous_scale=["#fb365c", "#111827", "#22d3ee"],
            hover_data={"performance": ":.2f"},
        )
        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%",
            marker=dict(line=dict(color="rgba(34,211,238,.45)", width=1)),
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(2,6,23,.85)",
            height=520,
            margin=dict(l=10, r=10, t=20, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        unavailable_box("Heatmap temporairement indisponible")

with tabs[7]:
    st.subheader("🌐 TradingView intégré")
    st.markdown(
        '<div class="notice">Module externe TradingView affiché uniquement pour visualisation. '
        "Les données principales de l'application restent basées sur yfinance.</div>",
        unsafe_allow_html=True,
    )
    url = f"https://s.tradingview.com/widgetembed/?symbol={tv_symbol(symbol)}&interval=D&theme=dark&style=1&locale=fr"
    components.iframe(url, height=620, scrolling=True)

with tabs[8]:
    st.subheader("⭐ Watchlist futuriste")

    col_add, col_clear = st.columns([2, 1])
    with col_add:
        if st.button("Ajouter à la watchlist", key="add_watchlist"):
            if symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(symbol)
                st.toast(f"{symbol} ajouté à la watchlist", icon="⭐")
            else:
                st.toast(f"{symbol} est déjà dans la watchlist", icon="☑️")
    with col_clear:
        if st.button("Effacer la watchlist", key="clear_watchlist"):
            st.session_state.watchlist = []
            st.toast("Watchlist effacée", icon="🧹")

    if st.session_state.watchlist:
        watch_rows = []
        for watch_symbol in st.session_state.watchlist:
            watch_hist = get_history(watch_symbol)
            watch_close = get_close_series(watch_hist)
            if len(watch_close) >= 2:
                watch_price = watch_close.iloc[-1]
                watch_change = ((watch_close.iloc[-1] - watch_close.iloc[-2]) / watch_close.iloc[-2]) * 100 if watch_close.iloc[-2] else 0
                watch_rows.append(
                    {
                        "Symbole": watch_symbol,
                        "Dernier prix": price_line(watch_price, currency),
                        "Variation jour": f"{watch_change:.2f}%",
                    }
                )
            else:
                watch_rows.append(
                    {
                        "Symbole": watch_symbol,
                        "Dernier prix": "Données temporairement indisponibles",
                        "Variation jour": "N/D",
                    }
                )
        st.dataframe(pd.DataFrame(watch_rows), use_container_width=True, hide_index=True)
    else:
        st.markdown(
            '<div class="data-missing">Aucun actif dans la watchlist. Ajoute un symbole pour construire ton tableau de bord nocturne.</div>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer">Stock Insight Neon — données publiques Yahoo Finance via yfinance, sans clé API payante. '
    "Sons synthétiques Web Audio API, sans fichier externe.</div>",
    unsafe_allow_html=True,
)
