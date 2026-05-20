import io
import json
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

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap:.55rem;
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stCaption {
    margin-bottom:.15rem;
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
    gap:8px;
    border-bottom:1px solid rgba(34,211,238,.18);
    overflow-x:auto;
    flex-wrap:wrap;
    scrollbar-width:thin;
    scrollbar-color:rgba(34,211,238,.55) rgba(15,23,42,.45);
}

.stTabs [data-baseweb="tab"] {
    background:rgba(15,23,42,.72);
    border:1px solid rgba(34,211,238,.20);
    border-radius:12px 12px 0 0;
    color:#e5e7eb;
    box-shadow:0 0 12px rgba(34,211,238,.06);
    min-height:42px;
    white-space:nowrap;
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

div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
section[data-testid="stSidebar"] button {
    min-height:44px;
}

section[data-testid="stSidebar"] div[data-testid="stSelectbox"],
section[data-testid="stSidebar"] div[data-testid="stTextInput"],
section[data-testid="stSidebar"] div.stButton {
    margin-bottom:.35rem;
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

@media (max-width: 1024px) {
    .block-container {
        padding:1.1rem .8rem 2rem;
    }

    .neon-title {
        font-size:34px;
    }

    .neon-subtitle {
        letter-spacing:.10em;
    }

    .card {
        padding:15px;
        margin-bottom:12px;
    }

    .kpi {
        padding:14px;
        min-height:96px;
    }

    .kpi-value {
        font-size:22px;
    }

    .stTabs [data-baseweb="tab-list"] {
        flex-wrap:nowrap;
        overflow-x:auto;
        padding-bottom:4px;
    }

    .stTabs [data-baseweb="tab"] {
        flex:0 0 auto;
        padding:8px 12px;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding:.8rem .55rem 1.5rem;
    }

    .neon-title {
        font-size:28px;
    }

    .notice, .data-missing, .mini-chip {
        padding:10px 12px;
        margin-bottom:12px;
    }

    div[data-testid="stMetric"] {
        padding:12px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


CATEGORIES = [
    "Tous",
    "Actions US",
    "Actions Europe",
    "Crypto",
    "ETF",
    "Forex",
    "Indices",
    "Matières premières",
]


POPULAR_ASSETS = [
    {"name": "Apple", "symbol": "AAPL", "category": "Actions US"},
    {"name": "Microsoft", "symbol": "MSFT", "category": "Actions US"},
    {"name": "Nvidia", "symbol": "NVDA", "category": "Actions US"},
    {"name": "Tesla", "symbol": "TSLA", "category": "Actions US"},
    {"name": "Amazon", "symbol": "AMZN", "category": "Actions US"},
    {"name": "Meta", "symbol": "META", "category": "Actions US"},
    {"name": "Google", "symbol": "GOOGL", "category": "Actions US"},
    {"name": "Netflix", "symbol": "NFLX", "category": "Actions US"},
    {"name": "AMD", "symbol": "AMD", "category": "Actions US"},
    {"name": "Intel", "symbol": "INTC", "category": "Actions US"},
    {"name": "Palantir", "symbol": "PLTR", "category": "Actions US"},
    {"name": "Coinbase", "symbol": "COIN", "category": "Actions US"},
    {"name": "Berkshire Hathaway", "symbol": "BRK-B", "category": "Actions US"},
    {"name": "Visa", "symbol": "V", "category": "Actions US"},
    {"name": "Mastercard", "symbol": "MA", "category": "Actions US"},
    {"name": "JPMorgan", "symbol": "JPM", "category": "Actions US"},
    {"name": "BlackRock", "symbol": "BLK", "category": "Actions US"},
    {"name": "McDonald's", "symbol": "MCD", "category": "Actions US"},
    {"name": "Coca-Cola", "symbol": "KO", "category": "Actions US"},
    {"name": "Pepsi", "symbol": "PEP", "category": "Actions US"},
    {"name": "Nike", "symbol": "NKE", "category": "Actions US"},
    {"name": "Walmart", "symbol": "WMT", "category": "Actions US"},
    {"name": "Costco", "symbol": "COST", "category": "Actions US"},
    {"name": "Eli Lilly", "symbol": "LLY", "category": "Actions US"},
    {"name": "Broadcom", "symbol": "AVGO", "category": "Actions US"},
    {"name": "Oracle", "symbol": "ORCL", "category": "Actions US"},
    {"name": "Salesforce", "symbol": "CRM", "category": "Actions US"},
    {"name": "Adobe", "symbol": "ADBE", "category": "Actions US"},
    {"name": "Cisco", "symbol": "CSCO", "category": "Actions US"},
    {"name": "Qualcomm", "symbol": "QCOM", "category": "Actions US"},
    {"name": "Texas Instruments", "symbol": "TXN", "category": "Actions US"},
    {"name": "Uber", "symbol": "UBER", "category": "Actions US"},
    {"name": "Shopify", "symbol": "SHOP", "category": "Actions US"},
    {"name": "Sea Limited", "symbol": "SE", "category": "Actions US"},
    {"name": "MercadoLibre", "symbol": "MELI", "category": "Actions US"},
    {"name": "LVMH", "symbol": "MC.PA", "category": "Actions Europe"},
    {"name": "TotalEnergies", "symbol": "TTE.PA", "category": "Actions Europe"},
    {"name": "Airbus", "symbol": "AIR.PA", "category": "Actions Europe"},
    {"name": "BNP Paribas", "symbol": "BNP.PA", "category": "Actions Europe"},
    {"name": "Schneider Electric", "symbol": "SU.PA", "category": "Actions Europe"},
    {"name": "Hermes", "symbol": "RMS.PA", "category": "Actions Europe"},
    {"name": "Safran", "symbol": "SAF.PA", "category": "Actions Europe"},
    {"name": "Sanofi", "symbol": "SAN.PA", "category": "Actions Europe"},
    {"name": "AXA", "symbol": "CS.PA", "category": "Actions Europe"},
    {"name": "Dassault Systemes", "symbol": "DSY.PA", "category": "Actions Europe"},
    {"name": "L'Oreal", "symbol": "OR.PA", "category": "Actions Europe"},
    {"name": "Kering", "symbol": "KER.PA", "category": "Actions Europe"},
    {"name": "Renault", "symbol": "RNO.PA", "category": "Actions Europe"},
    {"name": "Stellantis", "symbol": "STLAP.PA", "category": "Actions Europe"},
    {"name": "Societe Generale", "symbol": "GLE.PA", "category": "Actions Europe"},
    {"name": "Credit Agricole", "symbol": "ACA.PA", "category": "Actions Europe"},
    {"name": "Bitcoin", "symbol": "BTC-USD", "category": "Crypto"},
    {"name": "Ethereum", "symbol": "ETH-USD", "category": "Crypto"},
    {"name": "Solana", "symbol": "SOL-USD", "category": "Crypto"},
    {"name": "BNB", "symbol": "BNB-USD", "category": "Crypto"},
    {"name": "XRP", "symbol": "XRP-USD", "category": "Crypto"},
    {"name": "Dogecoin", "symbol": "DOGE-USD", "category": "Crypto"},
    {"name": "Cardano", "symbol": "ADA-USD", "category": "Crypto"},
    {"name": "Avalanche", "symbol": "AVAX-USD", "category": "Crypto"},
    {"name": "Chainlink", "symbol": "LINK-USD", "category": "Crypto"},
    {"name": "Polkadot", "symbol": "DOT-USD", "category": "Crypto"},
    {"name": "Polygon", "symbol": "MATIC-USD", "category": "Crypto"},
    {"name": "Litecoin", "symbol": "LTC-USD", "category": "Crypto"},
    {"name": "SPDR S&P 500 ETF", "symbol": "SPY", "category": "ETF"},
    {"name": "Invesco QQQ ETF", "symbol": "QQQ", "category": "ETF"},
    {"name": "Vanguard S&P 500 ETF", "symbol": "VOO", "category": "ETF"},
    {"name": "iShares MSCI World ETF", "symbol": "URTH", "category": "ETF"},
    {"name": "ARK Innovation ETF", "symbol": "ARKK", "category": "ETF"},
    {"name": "iShares Russell 2000 ETF", "symbol": "IWM", "category": "ETF"},
    {"name": "Financial Select Sector ETF", "symbol": "XLF", "category": "ETF"},
    {"name": "Technology Select Sector ETF", "symbol": "XLK", "category": "ETF"},
    {"name": "Energy Select Sector ETF", "symbol": "XLE", "category": "ETF"},
    {"name": "Gold ETF", "symbol": "GLD", "category": "ETF"},
    {"name": "EUR/USD", "symbol": "EURUSD=X", "category": "Forex"},
    {"name": "GBP/USD", "symbol": "GBPUSD=X", "category": "Forex"},
    {"name": "USD/JPY", "symbol": "JPY=X", "category": "Forex"},
    {"name": "USD/CHF", "symbol": "CHF=X", "category": "Forex"},
    {"name": "AUD/USD", "symbol": "AUDUSD=X", "category": "Forex"},
    {"name": "USD/CAD", "symbol": "CAD=X", "category": "Forex"},
    {"name": "NZD/USD", "symbol": "NZDUSD=X", "category": "Forex"},
    {"name": "EUR/GBP", "symbol": "EURGBP=X", "category": "Forex"},
    {"name": "S&P 500", "symbol": "^GSPC", "category": "Indices"},
    {"name": "Nasdaq 100", "symbol": "^NDX", "category": "Indices"},
    {"name": "Dow Jones", "symbol": "^DJI", "category": "Indices"},
    {"name": "Russell 2000", "symbol": "^RUT", "category": "Indices"},
    {"name": "CAC 40", "symbol": "^FCHI", "category": "Indices"},
    {"name": "DAX", "symbol": "^GDAXI", "category": "Indices"},
    {"name": "FTSE 100", "symbol": "^FTSE", "category": "Indices"},
    {"name": "Euro Stoxx 50", "symbol": "^STOXX50E", "category": "Indices"},
    {"name": "Nikkei 225", "symbol": "^N225", "category": "Indices"},
    {"name": "Hang Seng", "symbol": "^HSI", "category": "Indices"},
    {"name": "Gold Futures", "symbol": "GC=F", "category": "Matières premières"},
    {"name": "Silver Futures", "symbol": "SI=F", "category": "Matières premières"},
    {"name": "Copper Futures", "symbol": "HG=F", "category": "Matières premières"},
    {"name": "Oil WTI", "symbol": "CL=F", "category": "Matières premières"},
    {"name": "Brent Oil", "symbol": "BZ=F", "category": "Matières premières"},
    {"name": "Natural Gas", "symbol": "NG=F", "category": "Matières premières"},
    {"name": "Corn Futures", "symbol": "ZC=F", "category": "Matières premières"},
    {"name": "Soybean Futures", "symbol": "ZS=F", "category": "Matières premières"},
]


BASE_ASSETS = {asset["name"]: asset["symbol"] for asset in POPULAR_ASSETS}
ASSET_METADATA = {asset["symbol"]: asset for asset in POPULAR_ASSETS}


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
    for priority, asset in enumerate(POPULAR_ASSETS):
        rows.append(
            {
                "name": asset["name"],
                "symbol": asset["symbol"],
                "category": asset["category"],
                "type": asset["category"],
                "source": "Populaire",
                "priority": priority,
            }
        )

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
            for offset, (_, row) in enumerate(df.head(1500).iterrows()):
                symbol_value = str(row.get(symbol_col, "")).replace(".", "-").strip()
                asset_name = str(row.get(name_col, "")).strip()
                if symbol_value and symbol_value.lower() != "nan" and asset_name:
                    rows.append(
                        {
                            "name": asset_name,
                            "symbol": symbol_value,
                            "category": "Actions US",
                            "type": "Actions US",
                            "source": market_type,
                            "priority": 1000 + offset,
                        }
                    )
        except Exception:
            continue

    catalog_df = pd.DataFrame(rows).dropna()
    catalog_df = catalog_df[catalog_df["symbol"].astype(str).str.len() > 0]
    catalog_df = catalog_df.drop_duplicates("symbol")
    catalog_df = catalog_df.sort_values(["priority", "category", "name"], kind="stable").reset_index(drop=True)
    return catalog_df


def asset_label(row):
    return f"{row['symbol']} — {row['name']} [{row['category']}]"


def popular_slice(catalog_df, category="Tous", limit=60):
    popular = catalog_df[catalog_df["priority"] < 1000]
    if category != "Tous":
        popular = popular[popular["category"] == category]
    if popular.empty:
        popular = catalog_df if category == "Tous" else catalog_df[catalog_df["category"] == category]
    return popular.sort_values(["priority", "name"], kind="stable").head(limit)


def filter_catalog(catalog_df, category="Tous", query="", limit=80):
    scoped = catalog_df if category == "Tous" else catalog_df[catalog_df["category"] == category]
    if scoped.empty:
        return popular_slice(catalog_df, "Tous", limit), True

    q = str(query or "").lower().strip()
    if not q:
        return scoped.sort_values(["priority", "name"], kind="stable").head(limit), False

    filtered = scoped[
        scoped["name"].str.lower().str.contains(q, na=False, regex=False)
        | scoped["symbol"].str.lower().str.contains(q, na=False, regex=False)
        | scoped["category"].str.lower().str.contains(q, na=False, regex=False)
    ]
    if filtered.empty:
        return popular_slice(catalog_df, category, limit), True
    return filtered.sort_values(["priority", "name"], kind="stable").head(limit), False


def reset_asset_search():
    st.session_state.asset_category = "Tous"
    st.session_state.asset_search_text = ""
    st.session_state.selected_asset_symbol = "AAPL"


def fallback_currency(symbol):
    if symbol.endswith(".PA") or symbol in {"^FCHI", "^GDAXI", "^STOXX50E", "EURUSD=X", "EURGBP=X"}:
        return "EUR"
    if symbol.endswith("=X"):
        return "USD"
    return "USD"


def build_fallback_history(symbol):
    end = pd.Timestamp.utcnow().normalize()
    index = pd.bdate_range(end=end, periods=126)
    if index.empty:
        return pd.DataFrame()

    seed = sum((idx + 1) * ord(char) for idx, char in enumerate(symbol))
    base_price = {
        "AAPL": 190,
        "MSFT": 420,
        "NVDA": 950,
        "BTC-USD": 65000,
        "ETH-USD": 3400,
        "SPY": 520,
        "EURUSD=X": 1.08,
        "GC=F": 2350,
    }.get(symbol, 40 + (seed % 420))

    rows = []
    for idx, date_value in enumerate(index):
        wave = ((idx % 19) - 9) / 900
        drift = (idx - len(index) / 2) / 4200
        close_value = max(base_price * (1 + wave + drift + ((seed % 11) - 5) / 3000), 0.01)
        open_value = close_value * (1 - ((idx % 5) - 2) / 1200)
        high_value = max(open_value, close_value) * 1.006
        low_value = min(open_value, close_value) * 0.994
        rows.append(
            {
                "Open": open_value,
                "High": high_value,
                "Low": low_value,
                "Close": close_value,
                "Volume": int(750000 + (seed % 900000) + idx * 1200),
            }
        )

    data = pd.DataFrame(rows, index=index)
    data.attrs["is_fallback"] = True
    return data


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
            return build_fallback_history(symbol)

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        expected = ["Open", "High", "Low", "Close", "Volume"]
        for column in expected:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors="coerce")

        data = data.dropna(subset=["Close"])
        if data.empty:
            return build_fallback_history(symbol)
        data.attrs["is_fallback"] = False
        return data
    except Exception:
        return build_fallback_history(symbol)


@st.cache_data(ttl=3600, show_spinner=False)
def get_info(symbol):
    try:
        info = yf.Ticker(symbol).info
        if isinstance(info, dict):
            return info
        return {}
    except Exception:
        asset = ASSET_METADATA.get(symbol, {})
        return {
            "shortName": asset.get("name", symbol),
            "quoteType": asset.get("category", "N/D"),
            "currency": fallback_currency(symbol),
        }


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


def render_cyberpunk_audio(symbol, asset_name, asset_category, sound_enabled, voice_enabled, volume_level, hum_enabled):
    payload = json.dumps(
        {
            "soundEnabled": bool(sound_enabled),
            "voiceEnabled": bool(voice_enabled),
            "volumeLevel": volume_level,
            "humEnabled": bool(hum_enabled),
            "assetSymbol": symbol,
            "assetName": asset_name or symbol,
            "assetCategory": asset_category or "N/D",
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    components.html(
        r"""
<script>
(function () {
  const root = (function () {
    try {
      if (window.parent && window.parent !== window) return window.parent;
    } catch (e) {}
    return window;
  })();
  const doc = (function () {
    try {
      return root.document || document;
    } catch (e) {
      return document;
    }
  })();
  const incoming = __CONFIG__;
  const AudioContext = root.AudioContext || root.webkitAudioContext;
  const speech = root.speechSynthesis;

  const STATE = root.__stockInsightNeonAudio || {
    ctx: null,
    master: null,
    fxDelay: null,
    fxReturn: null,
    ambientGain: null,
    ambientNodes: [],
    bound: new WeakSet(),
    lastPlay: {},
    unlocked: false,
    setupDone: false,
    observerDone: false,
    voices: []
  };
  root.__stockInsightNeonAudio = STATE;
  STATE.config = Object.assign({
    soundEnabled: true,
    voiceEnabled: true,
    volumeLevel: "Moyen",
    humEnabled: true,
    assetSymbol: "AAPL",
    assetName: "Apple",
    assetCategory: "Actions US"
  }, incoming || {});

  function normalizeText(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[’']/g, "'")
      .toLowerCase();
  }

  function nodeText(node) {
    return normalizeText([
      node.innerText,
      node.value,
      node.getAttribute && node.getAttribute("aria-label"),
      node.getAttribute && node.getAttribute("title"),
      node.textContent
    ].filter(Boolean).join(" "));
  }

  function volumeScale() {
    const level = normalizeText(STATE.config.volumeLevel);
    if (level.includes("faible")) return 0.48;
    if (level.includes("fort")) return 1.05;
    return 0.76;
  }

  function canPlay() {
    return STATE.config.soundEnabled !== false && STATE.unlocked;
  }

  function setupAudioGraph() {
    if (!STATE.ctx || STATE.master) return;
    const ctx = STATE.ctx;
    const master = ctx.createGain();
    const compressor = ctx.createDynamicsCompressor();
    const delay = ctx.createDelay(0.28);
    const feedback = ctx.createGain();
    const fxReturn = ctx.createGain();

    master.gain.value = 0.92;
    compressor.threshold.value = -18;
    compressor.knee.value = 18;
    compressor.ratio.value = 5;
    compressor.attack.value = 0.004;
    compressor.release.value = 0.18;
    delay.delayTime.value = 0.085;
    feedback.gain.value = 0.18;
    fxReturn.gain.value = 0.18;

    delay.connect(feedback);
    feedback.connect(delay);
    delay.connect(fxReturn);
    fxReturn.connect(master);
    master.connect(compressor);
    compressor.connect(ctx.destination);

    STATE.master = master;
    STATE.fxDelay = delay;
    STATE.fxReturn = fxReturn;
  }

  function ensureAudio() {
    if (!AudioContext) return null;
    if (!STATE.ctx) STATE.ctx = new AudioContext();
    setupAudioGraph();
    if (STATE.ctx.state === "suspended") {
      STATE.ctx.resume().catch(function () {});
    }
    if (STATE.master) {
      STATE.master.gain.setTargetAtTime(0.9 * volumeScale(), STATE.ctx.currentTime, 0.025);
    }
    return STATE.ctx;
  }

  function output(node, wet) {
    if (!STATE.master) return;
    node.connect(STATE.master);
    if (STATE.fxDelay && wet > 0) {
      const send = STATE.ctx.createGain();
      send.gain.value = wet;
      node.connect(send);
      send.connect(STATE.fxDelay);
    }
  }

  function tone(options) {
    const ctx = ensureAudio();
    if (!ctx || !canPlay()) return;
    const now = ctx.currentTime + (options.start || 0);
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    const peak = Math.max(0.0001, (options.gain || 0.06) * volumeScale());
    const attack = options.attack || 0.012;
    const duration = options.duration || 0.12;

    osc.type = options.type || "sawtooth";
    osc.frequency.setValueAtTime(Math.max(1, options.freq || 120), now);
    if (options.toFreq) {
      osc.frequency.exponentialRampToValueAtTime(Math.max(1, options.toFreq), now + duration * 0.92);
    }
    if (options.detune) osc.detune.value = options.detune;

    filter.type = options.filterType || "lowpass";
    filter.frequency.setValueAtTime(options.filterFreq || 900, now);
    filter.Q.value = options.q === undefined ? 1.2 : options.q;
    if (options.toFilterFreq) {
      filter.frequency.exponentialRampToValueAtTime(Math.max(1, options.toFilterFreq), now + duration * 0.88);
    }

    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(peak, now + attack);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    osc.connect(filter);
    filter.connect(gain);
    output(gain, options.wet === undefined ? 0.18 : options.wet);
    osc.start(now);
    osc.stop(now + duration + 0.04);
  }

  function noiseBurst(options) {
    const ctx = ensureAudio();
    if (!ctx || !canPlay()) return;
    const duration = options.duration || 0.12;
    const start = ctx.currentTime + (options.start || 0);
    const length = Math.max(1, Math.floor(ctx.sampleRate * duration));
    const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / length);
    }
    const source = ctx.createBufferSource();
    const filter = ctx.createBiquadFilter();
    const gain = ctx.createGain();
    source.buffer = buffer;
    filter.type = options.filterType || "bandpass";
    filter.frequency.value = options.filterFreq || 900;
    filter.Q.value = options.q === undefined ? 2.5 : options.q;
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime((options.gain || 0.06) * volumeScale(), start + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
    source.connect(filter);
    filter.connect(gain);
    output(gain, options.wet === undefined ? 0.24 : options.wet);
    source.start(start);
    source.stop(start + duration + 0.02);
  }

  function metalHit(start, strength) {
    const offset = start || 0;
    const power = strength || 1;
    tone({ start: offset, freq: 86, toFreq: 42, duration: 0.34, type: "sine", gain: 0.16 * power, filterFreq: 180, wet: 0.28 });
    tone({ start: offset + 0.01, freq: 188, toFreq: 122, duration: 0.18, type: "triangle", gain: 0.055 * power, filterType: "bandpass", filterFreq: 360, q: 5.5, wet: 0.22 });
    tone({ start: offset + 0.018, freq: 317, toFreq: 228, duration: 0.16, type: "square", gain: 0.030 * power, filterType: "bandpass", filterFreq: 740, q: 7, wet: 0.25 });
    noiseBurst({ start: offset, duration: 0.13, gain: 0.075 * power, filterType: "highpass", filterFreq: 1150, q: 0.9, wet: 0.34 });
  }

  function tabOpen() {
    metalHit(0, 0.62);
    tone({ start: 0.035, freq: 420, toFreq: 690, duration: 0.09, type: "sawtooth", gain: 0.038, filterType: "bandpass", filterFreq: 850, q: 6, wet: 0.16 });
  }

  function assetChange() {
    tone({ start: 0, freq: 152, toFreq: 78, duration: 0.18, type: "triangle", gain: 0.075, filterFreq: 300, wet: 0.2 });
    tone({ start: 0.055, freq: 540, toFreq: 390, duration: 0.07, type: "square", gain: 0.030, filterType: "bandpass", filterFreq: 740, q: 7, wet: 0.12 });
    tone({ start: 0.125, freq: 690, toFreq: 460, duration: 0.08, type: "square", gain: 0.024, filterType: "bandpass", filterFreq: 920, q: 8, wet: 0.12 });
  }

  function scanSweep() {
    tone({ start: 0, freq: 54, toFreq: 78, duration: 0.72, type: "sine", gain: 0.105, filterFreq: 170, wet: 0.24 });
    tone({ start: 0.02, freq: 132, toFreq: 1180, duration: 0.66, type: "sawtooth", gain: 0.070, filterType: "bandpass", filterFreq: 360, toFilterFreq: 2600, q: 8.5, wet: 0.24 });
    tone({ start: 0.16, freq: 92, toFreq: 48, duration: 0.44, type: "triangle", gain: 0.065, filterFreq: 220, wet: 0.2 });
    noiseBurst({ start: 0.04, duration: 0.28, gain: 0.035, filterType: "bandpass", filterFreq: 1700, q: 6, wet: 0.26 });
    noiseBurst({ start: 0.31, duration: 0.18, gain: 0.032, filterType: "bandpass", filterFreq: 2350, q: 7, wet: 0.22 });
    metalHit(0.56, 0.7);
  }

  function watchAdd() {
    tone({ start: 0, freq: 110, toFreq: 82, duration: 0.18, type: "sine", gain: 0.09, filterFreq: 210, wet: 0.16 });
    tone({ start: 0.035, freq: 330, toFreq: 440, duration: 0.08, type: "triangle", gain: 0.040, filterType: "bandpass", filterFreq: 620, q: 5, wet: 0.16 });
    tone({ start: 0.105, freq: 495, toFreq: 660, duration: 0.10, type: "triangle", gain: 0.034, filterType: "bandpass", filterFreq: 940, q: 5.5, wet: 0.18 });
    tone({ start: 0.18, freq: 132, duration: 0.22, type: "sine", gain: 0.065, filterFreq: 260, wet: 0.26 });
  }

  function watchRemove() {
    tone({ start: 0, freq: 170, toFreq: 62, duration: 0.32, type: "sawtooth", gain: 0.09, filterFreq: 300, wet: 0.28 });
    tone({ start: 0.02, freq: 260, toFreq: 180, duration: 0.15, type: "square", gain: 0.035, filterType: "bandpass", filterFreq: 500, q: 6.5, wet: 0.2 });
    noiseBurst({ start: 0.04, duration: 0.12, gain: 0.060, filterType: "highpass", filterFreq: 820, q: 1.1, wet: 0.32 });
  }

  function searchPulse() {
    tone({ start: 0, freq: 72, toFreq: 60, duration: 0.28, type: "sine", gain: 0.085, filterFreq: 170, wet: 0.2 });
    tone({ start: 0.015, freq: 260, toFreq: 980, duration: 0.22, type: "sawtooth", gain: 0.045, filterType: "bandpass", filterFreq: 520, toFilterFreq: 1850, q: 7, wet: 0.24 });
    noiseBurst({ start: 0.18, duration: 0.10, gain: 0.025, filterType: "bandpass", filterFreq: 2100, q: 8, wet: 0.18 });
  }

  function errorAlert() {
    tone({ start: 0, freq: 146, toFreq: 76, duration: 0.34, type: "sawtooth", gain: 0.090, filterFreq: 280, wet: 0.30 });
    tone({ start: 0.04, freq: 233, toFreq: 210, duration: 0.21, type: "square", gain: 0.038, filterType: "bandpass", filterFreq: 430, q: 7, wet: 0.24 });
    tone({ start: 0.11, freq: 198, toFreq: 162, duration: 0.19, type: "square", gain: 0.032, filterType: "bandpass", filterFreq: 390, q: 7, wet: 0.24 });
    noiseBurst({ start: 0.03, duration: 0.18, gain: 0.052, filterType: "bandpass", filterFreq: 700, q: 3.4, wet: 0.34 });
  }

  function successConfirm() {
    tone({ start: 0, freq: 82, toFreq: 68, duration: 0.24, type: "sine", gain: 0.090, filterFreq: 180, wet: 0.18 });
    tone({ start: 0.045, freq: 246, duration: 0.18, type: "triangle", gain: 0.034, filterType: "bandpass", filterFreq: 520, q: 5, wet: 0.18 });
    tone({ start: 0.075, freq: 369, duration: 0.20, type: "triangle", gain: 0.027, filterType: "bandpass", filterFreq: 820, q: 5, wet: 0.2 });
  }

  function hoverTick() {
    tone({ start: 0, freq: 290, toFreq: 190, duration: 0.055, type: "triangle", gain: 0.020, filterType: "bandpass", filterFreq: 480, q: 5.5, wet: 0.12 });
    tone({ start: 0.005, freq: 72, duration: 0.060, type: "sine", gain: 0.018, filterFreq: 150, wet: 0.08 });
  }

  function tradingPortal() {
    metalHit(0, 1.0);
    tone({ start: 0.08, freq: 96, toFreq: 58, duration: 0.42, type: "sine", gain: 0.110, filterFreq: 190, wet: 0.34 });
    tone({ start: 0.12, freq: 420, toFreq: 1280, duration: 0.28, type: "sawtooth", gain: 0.050, filterType: "bandpass", filterFreq: 700, toFilterFreq: 2200, q: 8, wet: 0.28 });
  }

  function startHum() {
    const ctx = ensureAudio();
    if (!ctx || STATE.ambientNodes.length) {
      updateHum();
      return;
    }
    const gain = ctx.createGain();
    gain.gain.value = 0;
    gain.connect(STATE.master);
    STATE.ambientGain = gain;

    [41, 55, 109].forEach(function (freq, index) {
      const osc = ctx.createOscillator();
      const filter = ctx.createBiquadFilter();
      osc.type = index === 2 ? "triangle" : "sine";
      osc.frequency.value = freq;
      osc.detune.value = index === 1 ? -7 : 5;
      filter.type = "lowpass";
      filter.frequency.value = index === 2 ? 240 : 140;
      osc.connect(filter);
      filter.connect(gain);
      osc.start();
      STATE.ambientNodes.push(osc);
    });

    const buffer = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * 0.18;
    }
    const noise = ctx.createBufferSource();
    const noiseFilter = ctx.createBiquadFilter();
    noise.buffer = buffer;
    noise.loop = true;
    noiseFilter.type = "bandpass";
    noiseFilter.frequency.value = 880;
    noiseFilter.Q.value = 0.7;
    noise.connect(noiseFilter);
    noiseFilter.connect(gain);
    noise.start();
    STATE.ambientNodes.push(noise);
    updateHum();
  }

  function updateHum() {
    if (!STATE.ambientGain || !STATE.ctx) return;
    const target = (STATE.config.soundEnabled !== false && STATE.config.humEnabled !== false && STATE.unlocked)
      ? 0.018 * volumeScale()
      : 0;
    STATE.ambientGain.gain.setTargetAtTime(target, STATE.ctx.currentTime, 0.35);
  }

  function chooseVoice() {
    if (!speech) return null;
    const voices = speech.getVoices ? speech.getVoices() : [];
    STATE.voices = voices;
    const preferred = [
      "Microsoft David", "Microsoft Guy", "Google US English", "Daniel", "Alex",
      "Samantha", "Google UK English Male"
    ];
    for (const name of preferred) {
      const found = voices.find(function (voice) {
        return voice.name && voice.name.toLowerCase().includes(name.toLowerCase());
      });
      if (found) return found;
    }
    return voices.find(function (voice) { return /^en[-_]/i.test(voice.lang || ""); }) || voices[0] || null;
  }

  function cleanAssetName() {
    const raw = String(STATE.config.assetName || STATE.config.assetSymbol || "asset");
    return raw.replace(/\s+\[[^\]]+\]$/, "").replace(/\s+/g, " ").trim().slice(0, 80);
  }

  function voicePhrase(assetName) {
    const phrases = [
      "Scanning " + assetName + ".",
      "Analyzing " + assetName + ".",
      "Market scan initiated: " + assetName + ".",
      "Asset analysis launched: " + assetName + "."
    ];
    const seed = String(STATE.config.assetSymbol || assetName).split("").reduce(function (acc, char) {
      return acc + char.charCodeAt(0);
    }, 0);
    return phrases[seed % phrases.length];
  }

  function speakAnalysis() {
    if (!STATE.config.voiceEnabled || !speech || !STATE.unlocked) return;
    try {
      speech.cancel();
      if (speech.resume) speech.resume();
      const assetName = cleanAssetName();
      const utterance = new SpeechSynthesisUtterance(voicePhrase(assetName));
      const selectedVoice = chooseVoice();
      if (selectedVoice) utterance.voice = selectedVoice;
      utterance.lang = selectedVoice && selectedVoice.lang ? selectedVoice.lang : "en-US";
      utterance.pitch = 0.52;
      utterance.rate = 0.78;
      utterance.volume = Math.min(1, 0.86 * volumeScale());
      speech.speak(utterance);
      tone({ start: 0.02, freq: 64, duration: 1.15, type: "sine", gain: 0.025, filterFreq: 130, wet: 0.22 });
      tone({ start: 0.05, freq: 188, duration: 0.95, type: "triangle", gain: 0.012, filterType: "bandpass", filterFreq: 390, q: 4, wet: 0.28 });
    } catch (e) {}
  }
  STATE.speakAnalysis = speakAnalysis;

  function trigger(kind, options) {
    if (!canPlay()) return;
    const now = Date.now();
    const cooldown = kind === "hover" ? 140 : 80;
    if (STATE.lastPlay[kind] && now - STATE.lastPlay[kind] < cooldown) return;
    STATE.lastPlay[kind] = now;

    if (kind === "tab") tabOpen();
    else if (kind === "asset") assetChange();
    else if (kind === "scan") scanSweep();
    else if (kind === "watchAdd") watchAdd();
    else if (kind === "watchRemove") watchRemove();
    else if (kind === "search") searchPulse();
    else if (kind === "error") errorAlert();
    else if (kind === "success") successConfirm();
    else if (kind === "hover") hoverTick();
    else if (kind === "tradingView") tradingPortal();
    else if (kind === "analysis") {
      scanSweep();
      root.setTimeout(function () {
        const manager = root.__stockInsightNeonAudio;
        if (manager && typeof manager.speakAnalysis === "function") manager.speakAnalysis();
      }, options && options.voiceDelay ? options.voiceDelay : 560);
    }
  }

  function unlock() {
    STATE.unlocked = true;
    if (STATE.config.soundEnabled !== false) {
      ensureAudio();
      startHum();
    } else {
      updateHum();
    }
    if (speech && speech.resume) {
      try { speech.resume(); } catch (e) {}
    }
  }

  function classifyClick(node) {
    const role = node.getAttribute && node.getAttribute("role");
    const text = nodeText(node);
    if (role === "tab") return text.includes("tradingview") ? "tradingView" : "tab";
    if (role === "option") return "asset";
    if (role === "combobox") return "asset";
    if (text.includes("tradingview")) return "tradingView";
    if (text.includes("scanner") || text.includes("scan l") || (text.includes("lancer") && text.includes("analyse"))) return "analysis";
    if (text.includes("ajouter") && text.includes("watchlist")) return "watchAdd";
    if ((text.includes("effacer") || text.includes("supprimer") || text.includes("vider")) && text.includes("watchlist")) return "watchRemove";
    if (text.includes("recherche") || text.includes("palette") || text.includes("filtrer")) return "search";
    if (node.tagName === "BUTTON") return "tab";
    return null;
  }

  function bindSounds() {
    const nodes = doc.querySelectorAll("button, [role='tab'], [role='combobox'], [role='option'], input, a");
    nodes.forEach(function (node) {
      if (STATE.bound.has(node)) return;
      STATE.bound.add(node);

      node.addEventListener("click", function () {
        unlock();
        const kind = classifyClick(node);
        if (kind) trigger(kind, kind === "analysis" ? { voiceDelay: 560 } : undefined);
      }, { passive: true });

      node.addEventListener("keydown", function (event) {
        if (event.key !== "Enter") return;
        unlock();
        if (node.tagName === "INPUT") trigger("search");
      }, { passive: true });

      node.addEventListener("change", function () {
        unlock();
        if (node.tagName === "INPUT") trigger("search");
        else if ((node.getAttribute && node.getAttribute("role")) === "combobox") trigger("asset");
      }, { passive: true });

      node.addEventListener("pointerenter", function () {
        if (!canPlay()) return;
        const role = node.getAttribute && node.getAttribute("role");
        if (node.tagName === "BUTTON" || role === "tab" || role === "combobox" || node.tagName === "A") {
          trigger("hover");
        }
      }, { passive: true });
    });
  }

  function observeFeedback() {
    if (STATE.observerDone || !doc.body || !root.MutationObserver) return;
    STATE.observerDone = true;
    const observer = new root.MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (added) {
          if (!added || added.nodeType !== 1) return;
          const text = nodeText(added);
          const css = normalizeText(added.className || "");
          const testId = normalizeText(added.getAttribute && added.getAttribute("data-testid"));
          if (css.includes("data-missing") || text.includes("indisponible") || text.includes("erreur") || text.includes("error")) {
            trigger("error");
          } else if (
            testId.includes("toast") ||
            text.includes("ajoute") ||
            text.includes("efface") ||
            text.includes("verrouille") ||
            text.includes("lance")
          ) {
            trigger("success");
          }
        });
      });
    });
    observer.observe(doc.body, { childList: true, subtree: true });
  }

  function setupOnce() {
    if (STATE.setupDone) return;
    STATE.setupDone = true;
    ["pointerdown", "touchstart", "keydown"].forEach(function (eventName) {
      doc.addEventListener(eventName, unlock, { passive: true, capture: true });
    });
    if (speech && speech.addEventListener) {
      speech.addEventListener("voiceschanged", function () {
        STATE.voices = speech.getVoices ? speech.getVoices() : [];
      });
    }
  }

  setupOnce();
  bindSounds();
  observeFeedback();
  if (STATE.unlocked && STATE.config.soundEnabled !== false) startHum();
  else updateHum();
  if (!STATE.bindInterval) {
    STATE.bindInterval = root.setInterval(bindSounds, 900);
  }
})();
</script>
""".replace("__CONFIG__", payload),
        height=0,
    )


catalog = load_catalog()

if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "sound_volume" not in st.session_state:
    st.session_state.sound_volume = "Moyen"
if "cyberpunk_hum_enabled" not in st.session_state:
    st.session_state.cyberpunk_hum_enabled = True
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "asset_category" not in st.session_state:
    st.session_state.asset_category = "Tous"
if "asset_search_text" not in st.session_state:
    st.session_state.asset_search_text = ""
if "selected_asset_symbol" not in st.session_state:
    st.session_state.selected_asset_symbol = "AAPL"

with st.sidebar:
    st.markdown('<div class="neon-title">Stock Insight</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Neon Terminal</div>', unsafe_allow_html=True)
    st.caption("Radar financier cyberpunk sans API payante")
    st.markdown("---")

    with st.expander("🔊 Audio cyberpunk", expanded=False):
        st.checkbox("Activer les sons", key="sound_enabled")
        st.checkbox("Activer la voix", key="voice_enabled")
        st.radio(
            "Volume",
            ["Faible", "Moyen", "Fort"],
            horizontal=True,
            key="sound_volume",
        )
        st.checkbox("Hum cyberpunk léger", key="cyberpunk_hum_enabled")
        st.caption("Déblocage automatique après la première interaction, compatible iOS/Safari.")

    st.markdown("---")

    st.selectbox(
        "Catégorie d'actifs",
        CATEGORIES,
        key="asset_category",
        help="Filtre la palette avant de choisir un actif.",
    )
    query = st.text_input(
        "🔎 Filtrer la palette",
        key="asset_search_text",
        placeholder="Nom, symbole, crypto, ETF, forex...",
        help="Laisse vide pour afficher une liste prête à sélectionner.",
    )

    filtered, used_popular_fallback = filter_catalog(catalog, st.session_state.asset_category, query)
    if filtered.empty:
        filtered = popular_slice(catalog, "Tous", 60)
        used_popular_fallback = True

    labels = filtered.apply(asset_label, axis=1).tolist()
    symbol_by_label = dict(zip(labels, filtered["symbol"].tolist()))
    previous_symbol = st.session_state.get("selected_asset_symbol", "AAPL")
    default_index = 0
    if previous_symbol in filtered["symbol"].tolist():
        default_index = filtered["symbol"].tolist().index(previous_symbol)

    selected_label = st.selectbox(
        "🎛️ Palette de marché",
        labels,
        index=default_index,
        help="Sélecteur principal : ouvre la liste ou tape directement pour chercher dans les résultats.",
    )
    symbol = symbol_by_label.get(selected_label, "AAPL")
    st.session_state.selected_asset_symbol = symbol

    if used_popular_fallback:
        st.markdown(
            '<div class="notice">Aucun actif exact trouvé. La palette affiche les actifs populaires '
            "pour garder la navigation fluide.</div>",
            unsafe_allow_html=True,
        )

    col_launch, col_reset = st.columns([1, 1])
    with col_launch:
        if st.button("Lancer la recherche", key="launch_search"):
            st.toast(f"Palette verrouillée sur {symbol}", icon="🎛️")
    with col_reset:
        st.button("Réinitialiser la recherche", key="reset_asset_search", on_click=reset_asset_search)

    scanner_clicked = st.button("⚡ Scanner l’actif", key="scan_asset")
    if scanner_clicked:
        st.toast(f"Scan néon lancé pour {symbol}", icon="⚡")

    st.markdown("---")
    st.caption(f"Catalogue chargé : {len(catalog)} actifs · affichés : {len(filtered)}")
    st.caption("Historique cache : 2h · Catalogue : 24h")
    st.caption("Audio : Web Audio API + voix navigateur, sans fichier externe")


hist = get_history(symbol)
info = get_info(symbol)
close = get_close_series(hist)
data_available = not close.empty
history_is_fallback = bool(getattr(hist, "attrs", {}).get("is_fallback", False))
selected_asset = ASSET_METADATA.get(symbol, {})

name = info.get("longName") or info.get("shortName") or selected_asset.get("name") or symbol
sector = info.get("sector", "N/D")
industry = info.get("industry", "N/D")
country = info.get("country", "N/D")
currency = info.get("currency") or fallback_currency(symbol)
asset_type = info.get("quoteType") or selected_asset.get("category") or "N/D"
price = float(close.iloc[-1]) if data_available else None
previous = float(close.iloc[-2]) if len(close) > 1 else price
change = ((price - previous) / previous) * 100 if price is not None and previous else None

render_cyberpunk_audio(
    symbol=symbol,
    asset_name=name,
    asset_category=asset_type,
    sound_enabled=st.session_state.sound_enabled,
    voice_enabled=st.session_state.voice_enabled,
    volume_level=st.session_state.sound_volume,
    hum_enabled=st.session_state.cyberpunk_hum_enabled,
)


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
elif history_is_fallback:
    st.markdown(
        '<div class="notice">Mode continuité activé : Yahoo Finance est indisponible ou incomplet pour cet actif. '
        "L'interface reste utilisable avec une série locale indicative, sans bloquer l'application.</div>",
        unsafe_allow_html=True,
    )

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
    st.write(f"**Type :** {asset_type}")
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
    components.iframe(url, height=620, scrolling=False)

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
