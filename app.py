import io
import json
import time
import threading
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

# ============================================================
# CONFIG
# ============================================================
TOUCH_STABLE_PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": False,
    "responsive": True,
}

st.set_page_config(
    page_title="Analyse Boursière Neon",
    page_icon="📈",
    layout="wide"
)

# ============================================================
# API KEYS — from Streamlit secrets
# ============================================================
try:
    FINNHUB_KEY = st.secrets["FINNHUB_KEY"]
except Exception:
    FINNHUB_KEY = ""

try:
    ALPHA_VANTAGE_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
except Exception:
    ALPHA_VANTAGE_KEY = ""

# ============================================================
# CSS
# ============================================================
st.markdown("""
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

div.stButton > button {
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
}

.stTabs [data-baseweb="tab"] {
    background:rgba(15,23,42,.72);
    border:1px solid rgba(34,211,238,.20);
    border-radius:12px 12px 0 0;
    color:#e5e7eb;
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
}

input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
}

div[data-baseweb="select"] * {
    background-color: rgba(3,7,18,.96) !important;
    color: #f8fafc !important;
}

div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input {
    min-height:44px;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label {
    color: #e5e7eb !important;
    font-weight:800 !important;
}

div[data-testid="stMetric"] {
    background:rgba(8,13,28,.78);
    border:1px solid rgba(34,211,238,.22);
    border-radius:18px;
    padding:18px;
}

div[data-testid="stMetric"] label { color:#bae6fd !important; }

hr { border-color:rgba(34,211,238,.18) !important; }

.footer {
    color:#94a3b8;
    font-size:12px;
    font-family:"Courier New", monospace;
    text-align:center;
    margin-top:24px;
}

/* LIVE BADGE */
.live-badge {
    display:inline-block;
    background:rgba(0,255,65,.15);
    border:1px solid rgba(0,255,65,.4);
    color:#00ff41;
    font-size:10px;
    font-family:"Courier New", monospace;
    letter-spacing:2px;
    padding:3px 10px;
    border-radius:6px;
    animation:livePulse 2s ease-in-out infinite;
}

@keyframes livePulse {
    0%,100% { opacity:1; }
    50% { opacity:0.5; }
}

@media (max-width: 1024px) {
    .block-container { padding:1.1rem .8rem 2rem; }
    .neon-title { font-size:34px; }
    .kpi { padding:14px; min-height:96px; }
    .kpi-value { font-size:22px; }
}

@media (max-width: 640px) {
    .block-container { padding:.8rem .55rem 1.5rem; }
    .neon-title { font-size:28px; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# AUDIO SYSTEM — Improved cyberpunk music + action sounds
# ============================================================
def render_audio_system(asset_name, symbol):
    audio_html = """
<div id="stock-audio-root"></div>
<script>
(function() {
"use strict";

var ROOT_KEY = "__stockAudio";
var W = window.parent || window;
var D = W.document || document;
var S = W[ROOT_KEY] = W[ROOT_KEY] || {};

S.assetName = __ASSET_NAME__;
S.symbol = __SYMBOL__;
S.ctx = S.ctx || null;
S.playing = S.playing || false;
S.enabled = S.enabled !== undefined ? S.enabled : true;
S.volume = S.volume || "medium";
S.master = S.master || null;

var VOL = { low:0.04, medium:0.07, high:0.11 };
var VOLS = ["low","medium","high"];
var VLBL = { low:"faible", medium:"moyen", high:"fort" };

function getCtx() {
    var AC = W.AudioContext || W.webkitAudioContext || window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!S.ctx || S.ctx.state === "closed") S.ctx = new AC();
    if (S.ctx.state === "suspended") S.ctx.resume().catch(function(){});
    return S.ctx;
}

// ---- MAIN LAUNCH MUSIC ----
function playLaunchMusic() {
    var ctx = getCtx();
    if (!ctx || !S.enabled) return;
    var master = ctx.createGain();
    var comp = ctx.createDynamicsCompressor();
    master.gain.setValueAtTime(0.0001, ctx.currentTime);
    master.gain.linearRampToValueAtTime(VOL[S.volume], ctx.currentTime + 1.5);
    master.connect(comp);
    comp.connect(ctx.destination);
    S.master = master;

    // Bass drone
    [27.5, 32.7, 41.2].forEach(function(freq, i) {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        var f = ctx.createBiquadFilter();
        o.type = "sawtooth";
        o.frequency.value = freq;
        f.type = "lowpass";
        f.frequency.value = 200;
        g.gain.value = 0.35 - i*0.08;
        o.connect(f); f.connect(g); g.connect(master);
        o.start();
        // LFO
        var lfo = ctx.createOscillator();
        var lg = ctx.createGain();
        lfo.frequency.value = 0.05 + i*0.02;
        lg.gain.value = 0.08;
        lfo.connect(lg); lg.connect(g.gain);
        lfo.start();
    });

    // Synth pads — Vangelis style
    var chords = [
        [130.81, 164.81, 196.00, 261.63],
        [110.00, 138.59, 174.61, 220.00],
        [146.83, 185.00, 220.00, 293.66]
    ];

    chords.forEach(function(chord, ci) {
        var startTime = ctx.currentTime + ci * 4;
        chord.forEach(function(note, ni) {
            var o = ctx.createOscillator();
            var g = ctx.createGain();
            var f = ctx.createBiquadFilter();
            o.type = ni % 2 ? "triangle" : "sine";
            o.frequency.value = note;
            o.detune.value = (ni - 1.5) * 4;
            f.type = "lowpass";
            f.frequency.value = 800 + ni*100;
            g.gain.setValueAtTime(0.0001, startTime);
            g.gain.linearRampToValueAtTime(0.012 - ni*0.002, startTime + 2);
            g.gain.exponentialRampToValueAtTime(0.0001, startTime + 6);
            o.connect(f); f.connect(g); g.connect(master);
            o.start(startTime);
            o.stop(startTime + 7);
        });
    });

    // Rain noise
    var bufLen = ctx.sampleRate * 4;
    var buf = ctx.createBuffer(1, bufLen, ctx.sampleRate);
    var data = buf.getChannelData(0);
    for (var i = 0; i < bufLen; i++) data[i] = (Math.random()*2-1)*0.3;
    var rain = ctx.createBufferSource();
    rain.buffer = buf;
    rain.loop = true;
    var rf = ctx.createBiquadFilter();
    rf.type = "bandpass";
    rf.frequency.value = 4000;
    rf.Q.value = 0.5;
    var rg = ctx.createGain();
    rg.gain.value = 0.04;
    rain.connect(rf); rf.connect(rg); rg.connect(master);
    rain.start();

    // Neon buzz
    var buzz = ctx.createOscillator();
    var bg = ctx.createGain();
    buzz.type = "square";
    buzz.frequency.value = 120;
    bg.gain.value = 0.005;
    buzz.connect(bg); bg.connect(master);
    buzz.start();

    // Market ticker clicks
    function tick() {
        if (!S.playing || !S.enabled) return;
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        o.type = "square";
        o.frequency.value = 600 + Math.random()*600;
        g.gain.value = 0.015;
        g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.04);
        o.connect(g); g.connect(master);
        o.start(); o.stop(ctx.currentTime + 0.04);
        setTimeout(tick, 150 + Math.random()*700);
    }
    setTimeout(tick, 2000);

    S.playing = true;
    updatePanel();
}

// ---- SCAN SOUND — played when selecting an asset ----
function playScanSound() {
    var ctx = getCtx();
    if (!ctx || !S.enabled) return;
    var now = ctx.currentTime;
    var dest = S.master || ctx.destination;

    // Impact
    var o1 = ctx.createOscillator();
    var g1 = ctx.createGain();
    o1.type = "sine";
    o1.frequency.setValueAtTime(60, now);
    o1.frequency.exponentialRampToValueAtTime(30, now + 0.4);
    g1.gain.setValueAtTime(0.18, now);
    g1.gain.exponentialRampToValueAtTime(0.0001, now + 0.5);
    o1.connect(g1); g1.connect(ctx.destination);
    o1.start(now); o1.stop(now + 0.5);

    // Rise sweep
    var o2 = ctx.createOscillator();
    var g2 = ctx.createGain();
    var f2 = ctx.createBiquadFilter();
    o2.type = "sawtooth";
    o2.frequency.setValueAtTime(80, now + 0.1);
    o2.frequency.exponentialRampToValueAtTime(1200, now + 0.8);
    f2.type = "bandpass";
    f2.frequency.value = 800;
    f2.Q.value = 5;
    g2.gain.setValueAtTime(0.0001, now + 0.1);
    g2.gain.exponentialRampToValueAtTime(0.06, now + 0.3);
    g2.gain.exponentialRampToValueAtTime(0.0001, now + 0.9);
    o2.connect(f2); f2.connect(g2); g2.connect(ctx.destination);
    o2.start(now + 0.1); o2.stop(now + 1);

    // Terminal beeps
    [0.15, 0.22, 0.29, 0.36, 0.43].forEach(function(delay, i) {
        var o = ctx.createOscillator();
        var g = ctx.createGain();
        var freq = [523, 659, 784, 1047, 1319][i];
        o.type = "square";
        o.frequency.value = freq;
        g.gain.setValueAtTime(0.025, now + delay);
        g.gain.exponentialRampToValueAtTime(0.0001, now + delay + 0.06);
        o.connect(g); g.connect(ctx.destination);
        o.start(now + delay); o.stop(now + delay + 0.07);
    });

    // Voice announcement
    speak("Scanning " + S.assetName);
}

function speak(text) {
    var synth = W.speechSynthesis || window.speechSynthesis;
    if (!synth) return;
    try {
        synth.cancel();
        var u = new (W.SpeechSynthesisUtterance || window.SpeechSynthesisUtterance)(text);
        u.lang = "en-US";
        u.rate = 0.65;
        u.pitch = 0.3;
        u.volume = S.volume === "low" ? 0.6 : 0.85;
        var voices = synth.getVoices ? synth.getVoices() : [];
        var preferred = ["daniel","alex","google uk english male","microsoft david"];
        for (var p of preferred) {
            var v = voices.find(function(x){ return x.name && x.name.toLowerCase().includes(p); });
            if (v) { u.voice = v; break; }
        }
        synth.speak(u);
    } catch(e) {}
}

function stopMusic() {
    if (!S.master || !S.ctx) return;
    var now = S.ctx.currentTime;
    S.master.gain.cancelScheduledValues(now);
    S.master.gain.setValueAtTime(S.master.gain.value || 0.07, now);
    S.master.gain.exponentialRampToValueAtTime(0.0001, now + 0.5);
    S.playing = false;
    setTimeout(function() {
        try { S.master.disconnect(); } catch(e) {}
        S.master = null;
    }, 600);
}

function toggleAudio() {
    S.enabled = !S.enabled;
    try { W.localStorage.setItem("stockAudioEnabled", S.enabled); } catch(e) {}
    if (S.enabled) { playLaunchMusic(); }
    else { stopMusic(); try { (W.speechSynthesis||window.speechSynthesis).cancel(); } catch(e){} }
    updatePanel();
}

function cycleVolume() {
    var idx = VOLS.indexOf(S.volume);
    S.volume = VOLS[(idx+1) % VOLS.length];
    try { W.localStorage.setItem("stockAudioVolume", S.volume); } catch(e) {}
    if (S.master && S.ctx) {
        var now = S.ctx.currentTime;
        S.master.gain.cancelScheduledValues(now);
        S.master.gain.setValueAtTime(S.master.gain.value||0.07, now);
        S.master.gain.linearRampToValueAtTime(VOL[S.volume], now + 0.3);
    }
    updatePanel();
}

function updatePanel() {
    var btn = D.getElementById("audio-toggle");
    var vol = D.getElementById("audio-vol");
    if (btn) {
        btn.textContent = S.enabled ? "Ambiance: ON" : "Ambiance: OFF";
        btn.style.borderColor = S.enabled ? "rgba(34,211,238,.85)" : "rgba(34,211,238,.3)";
        btn.style.color = S.enabled ? "#ecfeff" : "#94a3b8";
        btn.style.boxShadow = S.enabled ? "0 0 20px rgba(34,211,238,.3)" : "none";
    }
    if (vol) vol.textContent = "Volume: " + VLBL[S.volume];
}

function installPanel() {
    var STYLE_ID = "stock-audio-style";
    if (!D.getElementById(STYLE_ID)) {
        var s = D.createElement("style");
        s.id = STYLE_ID;
        s.textContent = [
            ".saPanel{position:fixed;right:16px;bottom:16px;z-index:2147483000;display:flex;gap:8px;align-items:center;",
            "padding:8px 12px;border-radius:16px;border:1px solid rgba(34,211,238,.3);",
            "background:linear-gradient(135deg,rgba(1,4,12,.96),rgba(15,23,42,.93));",
            "box-shadow:0 0 24px rgba(34,211,238,.12);backdrop-filter:blur(12px)}",
            ".saLabel{color:#64748b;font:800 10px/1 'Courier New',monospace;letter-spacing:.1em;text-transform:uppercase;white-space:nowrap}",
            ".saBtn{min-height:40px;padding:8px 14px;border-radius:999px;border:1px solid rgba(34,211,238,.4);",
            "background:linear-gradient(135deg,rgba(3,7,18,.96),rgba(30,41,59,.92));color:#cbd5e1;",
            "font:800 11px/1.1 'Courier New',monospace;letter-spacing:.08em;text-transform:uppercase;",
            "cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent}",
            ".saBtn:active{transform:translateY(1px)}",
            "@media(max-width:640px){.saPanel{right:8px;bottom:8px;gap:6px;padding:6px}.saLabel{display:none}.saBtn{padding:8px 10px;font-size:10px}}"
        ].join("");
        D.head.appendChild(s);
    }

    var panel = D.getElementById("audio-panel");
    if (!panel) {
        panel = D.createElement("div");
        panel.id = "audio-panel";
        panel.className = "saPanel";
        D.body.appendChild(panel);
    }

    var label = D.getElementById("audio-label");
    if (!label) {
        label = D.createElement("span");
        label.id = "audio-label";
        label.className = "saLabel";
        label.textContent = "Audio tactique local";
        panel.appendChild(label);
    }

    var btn = D.getElementById("audio-toggle");
    if (!btn) {
        btn = D.createElement("button");
        btn.id = "audio-toggle";
        btn.className = "saBtn";
        btn.onclick = toggleAudio;
        panel.appendChild(btn);
    }

    var vol = D.getElementById("audio-vol");
    if (!vol) {
        vol = D.createElement("button");
        vol.id = "audio-vol";
        vol.className = "saBtn";
        vol.onclick = cycleVolume;
        panel.appendChild(vol);
    }

    updatePanel();
}

// Auto-start on first interaction
function unlock() {
    getCtx();
    if (S.enabled && !S.playing) playLaunchMusic();
}

["pointerdown","touchstart","keydown","click"].forEach(function(e) {
    D.addEventListener(e, unlock, {once:true, passive:true});
});

// Bind scan buttons
function bindButtons() {
    D.querySelectorAll("button").forEach(function(btn) {
        if (["audio-toggle","audio-vol"].includes(btn.id)) return;
        if (btn._audioBound) return;
        btn._audioBound = true;
        btn.addEventListener("click", function() {
            var t = (btn.innerText||btn.textContent||"").toLowerCase();
            if (t.includes("scanner") || t.includes("lancer") || t.includes("scan")) {
                playScanSound();
            }
        }, {passive:true});
    });
}

installPanel();
bindButtons();
setInterval(function() { installPanel(); bindButtons(); }, 1000);

// Load preferences
try {
    var savedEnabled = W.localStorage.getItem("stockAudioEnabled");
    if (savedEnabled !== null) S.enabled = savedEnabled === "true";
    var savedVol = W.localStorage.getItem("stockAudioVolume");
    if (savedVol && VOLS.includes(savedVol)) S.volume = savedVol;
} catch(e) {}

updatePanel();

})();
</script>
""".replace("__ASSET_NAME__", json.dumps(str(asset_name or symbol or "asset"))).replace("__SYMBOL__", json.dumps(str(symbol or "")))
    components.html(audio_html, height=1)

# ============================================================
# CATEGORIES & ASSETS
# ============================================================
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
    # Actions US
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
    {"name": "Paypal", "symbol": "PYPL", "category": "Actions US"},
    {"name": "Block (Square)", "symbol": "SQ", "category": "Actions US"},
    {"name": "Spotify", "symbol": "SPOT", "category": "Actions US"},
    {"name": "Airbnb", "symbol": "ABNB", "category": "Actions US"},
    {"name": "Snowflake", "symbol": "SNOW", "category": "Actions US"},
    {"name": "CrowdStrike", "symbol": "CRWD", "category": "Actions US"},
    {"name": "Palo Alto Networks", "symbol": "PANW", "category": "Actions US"},
    {"name": "ServiceNow", "symbol": "NOW", "category": "Actions US"},
    {"name": "Datadog", "symbol": "DDOG", "category": "Actions US"},
    {"name": "Cloudflare", "symbol": "NET", "category": "Actions US"},
    {"name": "MongoDB", "symbol": "MDB", "category": "Actions US"},
    {"name": "Zoom", "symbol": "ZM", "category": "Actions US"},
    {"name": "Boeing", "symbol": "BA", "category": "Actions US"},
    {"name": "Lockheed Martin", "symbol": "LMT", "category": "Actions US"},
    {"name": "ExxonMobil", "symbol": "XOM", "category": "Actions US"},
    {"name": "Chevron", "symbol": "CVX", "category": "Actions US"},
    {"name": "Pfizer", "symbol": "PFE", "category": "Actions US"},
    {"name": "Moderna", "symbol": "MRNA", "category": "Actions US"},
    {"name": "Johnson & Johnson", "symbol": "JNJ", "category": "Actions US"},
    {"name": "Goldman Sachs", "symbol": "GS", "category": "Actions US"},
    {"name": "Morgan Stanley", "symbol": "MS", "category": "Actions US"},
    {"name": "Micron", "symbol": "MU", "category": "Actions US"},
    {"name": "Applied Materials", "symbol": "AMAT", "category": "Actions US"},
    {"name": "TSMC", "symbol": "TSM", "category": "Actions US"},
    {"name": "Sea Limited", "symbol": "SE", "category": "Actions US"},
    {"name": "MercadoLibre", "symbol": "MELI", "category": "Actions US"},
    {"name": "Disney", "symbol": "DIS", "category": "Actions US"},
    # Actions Europe
    {"name": "LVMH", "symbol": "MC.PA", "category": "Actions Europe"},
    {"name": "TotalEnergies", "symbol": "TTE.PA", "category": "Actions Europe"},
    {"name": "Airbus", "symbol": "AIR.PA", "category": "Actions Europe"},
    {"name": "BNP Paribas", "symbol": "BNP.PA", "category": "Actions Europe"},
    {"name": "Schneider Electric", "symbol": "SU.PA", "category": "Actions Europe"},
    {"name": "Hermès", "symbol": "RMS.PA", "category": "Actions Europe"},
    {"name": "Safran", "symbol": "SAF.PA", "category": "Actions Europe"},
    {"name": "Sanofi", "symbol": "SAN.PA", "category": "Actions Europe"},
    {"name": "AXA", "symbol": "CS.PA", "category": "Actions Europe"},
    {"name": "Dassault Systèmes", "symbol": "DSY.PA", "category": "Actions Europe"},
    {"name": "L'Oréal", "symbol": "OR.PA", "category": "Actions Europe"},
    {"name": "Kering", "symbol": "KER.PA", "category": "Actions Europe"},
    {"name": "Renault", "symbol": "RNO.PA", "category": "Actions Europe"},
    {"name": "Société Générale", "symbol": "GLE.PA", "category": "Actions Europe"},
    {"name": "Crédit Agricole", "symbol": "ACA.PA", "category": "Actions Europe"},
    {"name": "Danone", "symbol": "BN.PA", "category": "Actions Europe"},
    {"name": "Michelin", "symbol": "ML.PA", "category": "Actions Europe"},
    {"name": "Capgemini", "symbol": "CAP.PA", "category": "Actions Europe"},
    {"name": "ASML", "symbol": "ASML", "category": "Actions Europe"},
    {"name": "SAP", "symbol": "SAP", "category": "Actions Europe"},
    {"name": "Siemens", "symbol": "SIEGY", "category": "Actions Europe"},
    {"name": "Volkswagen", "symbol": "VWAGY", "category": "Actions Europe"},
    {"name": "BMW", "symbol": "BMWYY", "category": "Actions Europe"},
    {"name": "Nestlé", "symbol": "NSRGY", "category": "Actions Europe"},
    {"name": "Novartis", "symbol": "NVS", "category": "Actions Europe"},
    {"name": "Roche", "symbol": "RHHBY", "category": "Actions Europe"},
    {"name": "HSBC", "symbol": "HSBC", "category": "Actions Europe"},
    {"name": "BP", "symbol": "BP", "category": "Actions Europe"},
    {"name": "Shell", "symbol": "SHEL", "category": "Actions Europe"},
    {"name": "Unilever", "symbol": "UL", "category": "Actions Europe"},
    # Crypto
    {"name": "Bitcoin (BTC)", "symbol": "BTC-USD", "category": "Crypto"},
    {"name": "Ethereum (ETH)", "symbol": "ETH-USD", "category": "Crypto"},
    {"name": "BNB", "symbol": "BNB-USD", "category": "Crypto"},
    {"name": "Solana (SOL)", "symbol": "SOL-USD", "category": "Crypto"},
    {"name": "XRP", "symbol": "XRP-USD", "category": "Crypto"},
    {"name": "Dogecoin (DOGE)", "symbol": "DOGE-USD", "category": "Crypto"},
    {"name": "Cardano (ADA)", "symbol": "ADA-USD", "category": "Crypto"},
    {"name": "Avalanche (AVAX)", "symbol": "AVAX-USD", "category": "Crypto"},
    {"name": "Chainlink (LINK)", "symbol": "LINK-USD", "category": "Crypto"},
    {"name": "Polkadot (DOT)", "symbol": "DOT-USD", "category": "Crypto"},
    {"name": "Polygon (MATIC)", "symbol": "MATIC-USD", "category": "Crypto"},
    {"name": "Litecoin (LTC)", "symbol": "LTC-USD", "category": "Crypto"},
    {"name": "Shiba Inu (SHIB)", "symbol": "SHIB-USD", "category": "Crypto"},
    {"name": "TRON (TRX)", "symbol": "TRX-USD", "category": "Crypto"},
    {"name": "Stellar (XLM)", "symbol": "XLM-USD", "category": "Crypto"},
    {"name": "Monero (XMR)", "symbol": "XMR-USD", "category": "Crypto"},
    {"name": "Cosmos (ATOM)", "symbol": "ATOM-USD", "category": "Crypto"},
    {"name": "Uniswap (UNI)", "symbol": "UNI-USD", "category": "Crypto"},
    {"name": "Ethereum Classic (ETC)", "symbol": "ETC-USD", "category": "Crypto"},
    {"name": "Filecoin (FIL)", "symbol": "FIL-USD", "category": "Crypto"},
    {"name": "Aave (AAVE)", "symbol": "AAVE-USD", "category": "Crypto"},
    {"name": "Maker (MKR)", "symbol": "MKR-USD", "category": "Crypto"},
    {"name": "Compound (COMP)", "symbol": "COMP-USD", "category": "Crypto"},
    {"name": "Curve (CRV)", "symbol": "CRV-USD", "category": "Crypto"},
    {"name": "Quant (QNT)", "symbol": "QNT-USD", "category": "Crypto"},
    {"name": "Render (RNDR)", "symbol": "RNDR-USD", "category": "Crypto"},
    {"name": "Injective (INJ)", "symbol": "INJ-USD", "category": "Crypto"},
    {"name": "Arbitrum (ARB)", "symbol": "ARB-USD", "category": "Crypto"},
    {"name": "Optimism (OP)", "symbol": "OP-USD", "category": "Crypto"},
    {"name": "Aptos (APT)", "symbol": "APT-USD", "category": "Crypto"},
    {"name": "Sui (SUI)", "symbol": "SUI-USD", "category": "Crypto"},
    {"name": "Pepe (PEPE)", "symbol": "PEPE-USD", "category": "Crypto"},
    {"name": "Bitcoin Cash (BCH)", "symbol": "BCH-USD", "category": "Crypto"},
    {"name": "Dash (DASH)", "symbol": "DASH-USD", "category": "Crypto"},
    {"name": "Zcash (ZEC)", "symbol": "ZEC-USD", "category": "Crypto"},
    {"name": "Algorand (ALGO)", "symbol": "ALGO-USD", "category": "Crypto"},
    {"name": "VeChain (VET)", "symbol": "VET-USD", "category": "Crypto"},
    {"name": "Internet Computer (ICP)", "symbol": "ICP-USD", "category": "Crypto"},
    {"name": "Hedera (HBAR)", "symbol": "HBAR-USD", "category": "Crypto"},
    {"name": "Near Protocol (NEAR)", "symbol": "NEAR-USD", "category": "Crypto"},
    {"name": "Fantom (FTM)", "symbol": "FTM-USD", "category": "Crypto"},
    {"name": "Decentraland (MANA)", "symbol": "MANA-USD", "category": "Crypto"},
    {"name": "Sandbox (SAND)", "symbol": "SAND-USD", "category": "Crypto"},
    {"name": "Axie Infinity (AXS)", "symbol": "AXS-USD", "category": "Crypto"},
    {"name": "1inch (1INCH)", "symbol": "1INCH-USD", "category": "Crypto"},
    {"name": "SushiSwap (SUSHI)", "symbol": "SUSHI-USD", "category": "Crypto"},
    {"name": "Yearn Finance (YFI)", "symbol": "YFI-USD", "category": "Crypto"},
    {"name": "Floki (FLOKI)", "symbol": "FLOKI-USD", "category": "Crypto"},
    {"name": "Bonk (BONK)", "symbol": "BONK-USD", "category": "Crypto"},
    # ETF
    {"name": "SPDR S&P 500 (SPY)", "symbol": "SPY", "category": "ETF"},
    {"name": "Invesco QQQ (QQQ)", "symbol": "QQQ", "category": "ETF"},
    {"name": "Vanguard S&P 500 (VOO)", "symbol": "VOO", "category": "ETF"},
    {"name": "iShares MSCI World (URTH)", "symbol": "URTH", "category": "ETF"},
    {"name": "ARK Innovation (ARKK)", "symbol": "ARKK", "category": "ETF"},
    {"name": "iShares Russell 2000 (IWM)", "symbol": "IWM", "category": "ETF"},
    {"name": "Financial Select (XLF)", "symbol": "XLF", "category": "ETF"},
    {"name": "Technology Select (XLK)", "symbol": "XLK", "category": "ETF"},
    {"name": "Energy Select (XLE)", "symbol": "XLE", "category": "ETF"},
    {"name": "Gold ETF (GLD)", "symbol": "GLD", "category": "ETF"},
    {"name": "Vanguard Total Market (VTI)", "symbol": "VTI", "category": "ETF"},
    {"name": "iShares Emerging (IEMG)", "symbol": "IEMG", "category": "ETF"},
    # Forex
    {"name": "EUR/USD", "symbol": "EURUSD=X", "category": "Forex"},
    {"name": "GBP/USD", "symbol": "GBPUSD=X", "category": "Forex"},
    {"name": "USD/JPY", "symbol": "JPY=X", "category": "Forex"},
    {"name": "USD/CHF", "symbol": "CHF=X", "category": "Forex"},
    {"name": "AUD/USD", "symbol": "AUDUSD=X", "category": "Forex"},
    {"name": "USD/CAD", "symbol": "CAD=X", "category": "Forex"},
    {"name": "NZD/USD", "symbol": "NZDUSD=X", "category": "Forex"},
    {"name": "EUR/GBP", "symbol": "EURGBP=X", "category": "Forex"},
    {"name": "EUR/JPY", "symbol": "EURJPY=X", "category": "Forex"},
    {"name": "USD/CNY", "symbol": "CNY=X", "category": "Forex"},
    # Indices
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
    {"name": "ASX 200", "symbol": "^AXJO", "category": "Indices"},
    {"name": "Sensex (Inde)", "symbol": "^BSESN", "category": "Indices"},
    # Matières premières
    {"name": "Gold (Or)", "symbol": "GC=F", "category": "Matières premières"},
    {"name": "Silver (Argent)", "symbol": "SI=F", "category": "Matières premières"},
    {"name": "Copper (Cuivre)", "symbol": "HG=F", "category": "Matières premières"},
    {"name": "Oil WTI", "symbol": "CL=F", "category": "Matières premières"},
    {"name": "Brent Oil", "symbol": "BZ=F", "category": "Matières premières"},
    {"name": "Natural Gas", "symbol": "NG=F", "category": "Matières premières"},
    {"name": "Corn (Maïs)", "symbol": "ZC=F", "category": "Matières premières"},
    {"name": "Wheat (Blé)", "symbol": "ZW=F", "category": "Matières premières"},
    {"name": "Soybean (Soja)", "symbol": "ZS=F", "category": "Matières premières"},
    {"name": "Platinum", "symbol": "PL=F", "category": "Matières premières"},
]

ASSET_METADATA = {a["symbol"]: a for a in POPULAR_ASSETS}
BASE_ASSETS = {a["name"]: a["symbol"] for a in POPULAR_ASSETS}

# ============================================================
# COINGECKO — All cryptos
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_cryptos():
    """Fetch all cryptos from CoinGecko — 10000+"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/list"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            cryptos = []
            for coin in data:
                sym = str(coin.get("symbol","")).upper() + "-USD"
                name = str(coin.get("name",""))
                if name and len(name) > 0:
                    cryptos.append({
                        "name": f"{name} ({coin.get('symbol','').upper()})",
                        "symbol": sym,
                        "category": "Crypto",
                        "source": "CoinGecko",
                        "priority": 500
                    })
            return cryptos[:10000]
    except Exception:
        pass
    return []

# ============================================================
# FINNHUB — All world stocks
# ============================================================
@st.cache_data(ttl=86400, show_spinner=False)
def get_finnhub_stocks():
    """Fetch all stocks from Finnhub — world exchanges"""
    if not FINNHUB_KEY:
        return []

    exchanges = ["US", "L", "PA", "DE", "T", "HK", "TO", "AS"]
    all_stocks = []

    for exchange in exchanges:
        try:
            url = f"https://finnhub.io/api/v1/stock/symbol?exchange={exchange}&token={FINNHUB_KEY}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for stock in data[:500]:
                    sym = str(stock.get("symbol","")).strip()
                    name = str(stock.get("description","")).strip()
                    if sym and name:
                        cat = "Actions US" if exchange == "US" else "Actions Europe" if exchange in ["L","PA","DE","AS"] else "Actions Asie"
                        all_stocks.append({
                            "name": f"{name}",
                            "symbol": sym,
                            "category": cat,
                            "source": f"Finnhub-{exchange}",
                            "priority": 200
                        })
        except Exception:
            continue

    return all_stocks

# ============================================================
# CATALOG
# ============================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_catalog():
    rows = []

    # Popular assets first
    for i, asset in enumerate(POPULAR_ASSETS):
        rows.append({
            "name": asset["name"],
            "symbol": asset["symbol"],
            "category": asset["category"],
            "type": asset["category"],
            "source": "Populaire",
            "priority": i
        })

    # Finnhub world stocks
    finnhub_stocks = get_finnhub_stocks()
    for stock in finnhub_stocks:
        rows.append({
            "name": stock["name"],
            "symbol": stock["symbol"],
            "category": stock["category"],
            "type": stock["category"],
            "source": stock["source"],
            "priority": stock["priority"]
        })

    # CoinGecko all cryptos
    all_cryptos = get_all_cryptos()
    for crypto in all_cryptos:
        rows.append({
            "name": crypto["name"],
            "symbol": crypto["symbol"],
            "category": "Crypto",
            "type": "Crypto",
            "source": "CoinGecko",
            "priority": 500
        })

    # NASDAQ listed
    try:
        r = requests.get(
            "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt",
            timeout=8
        )
        df = pd.read_csv(io.StringIO(r.text), sep="|")
        if "Test Issue" in df.columns:
            df = df[df["Test Issue"] == "N"]
        for _, row in df.head(3000).iterrows():
            sym = str(row.get("Symbol","")).strip()
            name = str(row.get("Security Name","")).strip()
            if sym and name and sym.lower() != "nan":
                rows.append({
                    "name": name, "symbol": sym,
                    "category": "Actions US", "type": "Actions US",
                    "source": "NASDAQ", "priority": 1000
                })
    except Exception:
        pass

    # NYSE/AMEX
    try:
        r = requests.get(
            "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt",
            timeout=8
        )
        df = pd.read_csv(io.StringIO(r.text), sep="|")
        if "Test Issue" in df.columns:
            df = df[df["Test Issue"] == "N"]
        for _, row in df.head(3000).iterrows():
            sym = str(row.get("ACT Symbol","")).replace(".","-").strip()
            name = str(row.get("Security Name","")).strip()
            if sym and name and sym.lower() != "nan":
                rows.append({
                    "name": name, "symbol": sym,
                    "category": "Actions US", "type": "Actions US",
                    "source": "NYSE", "priority": 1000
                })
    except Exception:
        pass

    catalog_df = pd.DataFrame(rows).dropna()
    catalog_df = catalog_df[catalog_df["symbol"].astype(str).str.len() > 0]
    catalog_df = catalog_df.drop_duplicates("symbol")
    catalog_df = catalog_df.sort_values(
        ["priority","category","name"], kind="stable"
    ).reset_index(drop=True)
    return catalog_df

# ============================================================
# HELPERS
# ============================================================
def safe_number(value, decimals=2, suffix=""):
    try:
        if value is None or pd.isna(value):
            return "N/D"
        return f"{float(value):.{decimals}f}{suffix}"
    except Exception:
        return "N/D"

def format_int(value):
    try:
        if value is None or pd.isna(value):
            return "N/D"
        return f"{int(float(value)):,}".replace(",", " ")
    except Exception:
        return "N/D"

def money(x):
    try:
        if x is None or pd.isna(x):
            return "N/D"
        x = float(x)
        if abs(x) >= 1e12: return f"${x/1e12:.2f}T"
        if abs(x) >= 1e9: return f"${x/1e9:.2f}B"
        if abs(x) >= 1e6: return f"${x/1e6:.2f}M"
        return f"${x:,.2f}"
    except Exception:
        return "N/D"

def fallback_currency(symbol):
    if symbol.endswith(".PA") or symbol in {"^FCHI","^GDAXI","^STOXX50E"}:
        return "EUR"
    return "USD"

def price_line(value, currency):
    try:
        return f"{float(value):,.2f} {currency}".replace(",", " ")
    except Exception:
        return "N/D"

def asset_label(row):
    return f"{row['symbol']} — {row['name']} [{row['category']}]"

def popular_slice(catalog_df, category="Tous", limit=60):
    pop = catalog_df[catalog_df["priority"] < 200]
    if category != "Tous":
        pop = pop[pop["category"] == category]
    if pop.empty:
        pop = catalog_df if category == "Tous" else catalog_df[catalog_df["category"] == category]
    return pop.sort_values(["priority","name"], kind="stable").head(limit)

def filter_catalog(catalog_df, category="Tous", query="", limit=80):
    scoped = catalog_df if category == "Tous" else catalog_df[catalog_df["category"] == category]
    if scoped.empty:
        return popular_slice(catalog_df, "Tous", limit), True
    q = str(query or "").lower().strip()
    if not q:
        return scoped.sort_values(["priority","name"], kind="stable").head(limit), False
    filtered = scoped[
        scoped["name"].str.lower().str.contains(q, na=False, regex=False) |
        scoped["symbol"].str.lower().str.contains(q, na=False, regex=False)
    ]
    if filtered.empty:
        return popular_slice(catalog_df, category, limit), True
    return filtered.sort_values(["priority","name"], kind="stable").head(limit), False

def reset_asset_search():
    st.session_state.asset_category = "Tous"
    st.session_state.asset_search_text = ""
    st.session_state.selected_asset_symbol = "AAPL"

def tv_symbol(symbol):
    if symbol.endswith("-USD"):
        return "CRYPTO:" + symbol.replace("-USD","USD")
    if symbol.endswith(".PA"):
        return "EURONEXT:" + symbol.replace(".PA","")
    if symbol.startswith("^"):
        return symbol
    return "NASDAQ:" + symbol

# ============================================================
# DATA FETCHING — with robust error handling
# ============================================================
def build_fallback_history(symbol):
    end = pd.Timestamp.utcnow().normalize()
    index = pd.bdate_range(end=end, periods=126)
    if index.empty:
        return pd.DataFrame()
    seed = sum((i+1)*ord(c) for i,c in enumerate(symbol))
    base = {"AAPL":190,"MSFT":420,"NVDA":950,"BTC-USD":65000,"ETH-USD":3400,"SPY":520}.get(symbol, 40+(seed%420))
    rows = []
    for i, d in enumerate(index):
        wave = ((i%19)-9)/900
        drift = (i-len(index)/2)/4200
        close = max(base*(1+wave+drift+((seed%11)-5)/3000), 0.01)
        open_ = close*(1-((i%5)-2)/1200)
        rows.append({
            "Open": open_, "High": max(open_,close)*1.006,
            "Low": min(open_,close)*0.994, "Close": close,
            "Volume": int(750000+(seed%900000)+i*1200)
        })
    data = pd.DataFrame(rows, index=index)
    data.attrs["is_fallback"] = True
    return data

@st.cache_data(ttl=300, show_spinner=False)
def get_history(symbol, period="6mo"):
    try:
        data = yf.download(symbol, period=period, progress=False, threads=False, auto_adjust=False)
        if data is None or data.empty:
            return build_fallback_history(symbol)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        for col in ["Open","High","Low","Close","Volume"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")
        data = data.dropna(subset=["Close"])
        if data.empty:
            return build_fallback_history(symbol)
        data.attrs["is_fallback"] = False
        return data
    except Exception:
        return build_fallback_history(symbol)

@st.cache_data(ttl=300, show_spinner=False)
def get_info(symbol):
    try:
        info = yf.Ticker(symbol).info
        if isinstance(info, dict) and len(info) > 3:
            return info
        return {}
    except Exception:
        asset = ASSET_METADATA.get(symbol, {})
        return {
            "shortName": asset.get("name", symbol),
            "quoteType": asset.get("category","N/D"),
            "currency": fallback_currency(symbol)
        }

@st.cache_data(ttl=30, show_spinner=False)
def get_live_price_finnhub(symbol):
    """Get live price from Finnhub"""
    if not FINNHUB_KEY:
        return None
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("c") and data["c"] > 0:
                return {
                    "price": data["c"],
                    "change": data.get("d", 0),
                    "change_pct": data.get("dp", 0),
                    "high": data.get("h", 0),
                    "low": data.get("l", 0),
                    "open": data.get("o", 0),
                    "prev_close": data.get("pc", 0)
                }
    except Exception:
        pass
    return None

@st.cache_data(ttl=60, show_spinner=False)
def get_live_crypto_coingecko(symbol):
    """Get live crypto price from CoinGecko"""
    try:
        coin_id = symbol.replace("-USD","").lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if coin_id in data:
                d = data[coin_id]
                return {
                    "price": d.get("usd", 0),
                    "change_pct": d.get("usd_24h_change", 0),
                    "volume": d.get("usd_24h_vol", 0),
                    "market_cap": d.get("usd_market_cap", 0)
                }
    except Exception:
        pass
    return None

def get_close_series(history):
    if history is None or history.empty or "Close" not in history.columns:
        return pd.Series(dtype="float64")
    close = history["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:,0]
    return pd.to_numeric(close, errors="coerce").dropna()

def kpi_card(title, value, tone=""):
    tone_class = f" {tone}" if tone else ""
    st.markdown(
        f'<div class="kpi"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value{tone_class}">{value}</div></div>',
        unsafe_allow_html=True
    )

def unavailable_box(msg="Données temporairement indisponibles"):
    st.markdown(
        f'<div class="data-missing">▣ {msg}. Réessaie dans quelques minutes.</div>',
        unsafe_allow_html=True
    )

# ============================================================
# LOAD CATALOG
# ============================================================
catalog = load_catalog()

# ============================================================
# SESSION STATE
# ============================================================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "asset_category" not in st.session_state:
    st.session_state.asset_category = "Tous"
if "asset_search_text" not in st.session_state:
    st.session_state.asset_search_text = ""
if "selected_asset_symbol" not in st.session_state:
    st.session_state.selected_asset_symbol = "AAPL"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="neon-title">Analyse<br>Boursière</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Terminal Néon</div>', unsafe_allow_html=True)
    st.caption("Radar financier cyberpunk sans API payante")
    st.markdown("---")

    st.selectbox(
        "Catégorie d'actifs",
        CATEGORIES,
        key="asset_category",
    )

    query = st.text_input(
        "🔎 Filtrer la palette",
        key="asset_search_text",
        placeholder="Nom, symbole, crypto, ETF, forex...",
    )

    filtered, used_fallback = filter_catalog(
        catalog, st.session_state.asset_category, query
    )
    if filtered.empty:
        filtered = popular_slice(catalog, "Tous", 60)
        used_fallback = True

    labels = filtered.apply(asset_label, axis=1).tolist()
    symbol_by_label = dict(zip(labels, filtered["symbol"].tolist()))
    name_by_symbol = dict(zip(filtered["symbol"].tolist(), filtered["name"].tolist()))

    prev_sym = st.session_state.get("selected_asset_symbol","AAPL")
    default_idx = 0
    if prev_sym in filtered["symbol"].tolist():
        default_idx = filtered["symbol"].tolist().index(prev_sym)

    selected_label = st.selectbox(
        "🎛️ Palette de marché",
        labels,
        index=default_idx,
    )
    symbol = symbol_by_label.get(selected_label, "AAPL")
    display_name = name_by_symbol.get(symbol, symbol)
    st.session_state.selected_asset_symbol = symbol

    if used_fallback:
        st.markdown(
            '<div class="notice">Aucun actif exact trouvé — palette populaire affichée.</div>',
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lancer la recherche"):
            st.toast(f"Palette verrouillée sur {symbol}", icon="🎛️")
    with col2:
        st.button("Réinitialiser la recherche", on_click=reset_asset_search)

    if st.button("⚡ Scanner l'actif"):
        st.toast(f"Scan lancé pour {symbol}", icon="⚡")

    st.markdown("---")

    # Live price in sidebar
    is_crypto = symbol.endswith("-USD")
    live_data = None

    if is_crypto:
        live_data = get_live_crypto_coingecko(symbol)
    else:
        live_data = get_live_price_finnhub(symbol)

    if live_data and live_data.get("price", 0) > 0:
        price_live = live_data["price"]
        chg = live_data.get("change_pct", 0) or 0
        arrow = "▲" if chg >= 0 else "▼"
        color = "#00ff41" if chg >= 0 else "#fb365c"
        st.markdown(
            f'<div style="text-align:center;padding:10px">'
            f'<div style="color:#94a3b8;font-size:10px;letter-spacing:2px;font-family:Courier New">PRIX LIVE</div>'
            f'<div style="color:#f8fafc;font-size:22px;font-weight:900">{price_live:,.2f}</div>'
            f'<div style="color:{color};font-size:14px">{arrow} {abs(chg):.2f}%</div>'
            f'<span class="live-badge">● LIVE</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.caption(f"📡 {symbol} — données live indisponibles")

    st.markdown("---")
    st.caption(f"📊 {len(catalog):,} actifs chargés")
    st.caption(f"🌍 Finnhub + CoinGecko + Yahoo Finance")
    st.caption("⏱ Live: 30s · Historique: 5min")

# ============================================================
# AUDIO
# ============================================================
render_audio_system(display_name, symbol)

# ============================================================
# MAIN DATA
# ============================================================
hist = get_history(symbol)
info = get_info(symbol)
close = get_close_series(hist)
data_available = not close.empty
is_fallback = bool(getattr(hist, "attrs", {}).get("is_fallback", False))
selected_asset = ASSET_METADATA.get(symbol, {})

name = info.get("longName") or info.get("shortName") or selected_asset.get("name") or symbol
sector = info.get("sector","N/D")
industry = info.get("industry","N/D")
country = info.get("country","N/D")
currency = info.get("currency") or fallback_currency(symbol)

# Use live price if available, else use history
if live_data and live_data.get("price",0) > 0:
    price = float(live_data["price"])
    change = float(live_data.get("change_pct", 0) or 0)
elif data_available:
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) > 1 else price
    change = ((price - prev) / prev * 100) if prev else 0
else:
    price = None
    change = None

# ============================================================
# HEADER
# ============================================================
st.markdown('<div class="neon-title">📈 Stock Insight Neon Terminal</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="terminal-line">MODE DETECTIVE FINANCIER · PLUIE SYNTHETIQUE · '
    f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")} · '
    f'{"🔴 LIVE" if live_data else "📊 HISTORIQUE"}</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="notice">⚠️ Analyse éducative — données publiques. Aucun conseil financier. Aucune API payante.</div>',
    unsafe_allow_html=True
)

st.title(name)
st.caption(f"{symbol} · {sector} · {industry} · {country}")

if is_fallback:
    st.markdown(
        '<div class="notice">Mode continuité : données Yahoo Finance indisponibles. '
        'Série indicative locale affichée.</div>',
        unsafe_allow_html=True
    )

# ============================================================
# TABS
# ============================================================
tabs = st.tabs([
    "🏠 Accueil",
    "🌍 Marché",
    "📈 Performance",
    "📊 Ratios",
    "⚠️ Risque",
    "🧠 Résumé",
    "🔥 Heatmap",
    "🌐 TradingView",
    "⭐ Watchlist",
])

# ---- TAB 0 — ACCUEIL ----
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Prix", price_line(price, currency) if price else "N/D")
    with c2:
        tone = "kpi-good" if change and change >= 0 else "kpi-bad"
        arrow = "▲" if change and change >= 0 else "▼"
        kpi_card("Variation", f"{arrow} {abs(change):.2f}%" if change is not None else "N/D", tone)
    with c3:
        kpi_card("Market Cap", money(info.get("marketCap")))
    with c4:
        kpi_card("Beta", safe_number(info.get("beta"), 2))

    if live_data:
        st.markdown('<span class="live-badge">● DONNÉES LIVE</span>', unsafe_allow_html=True)

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
        st.markdown("**Description :**")
        st.write(str(info.get("longBusinessSummary",""))[:800] + "...")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- TAB 1 — MARCHÉ ----
with tabs[1]:
    st.subheader("🌍 Marché")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Type :** {info.get('quoteType','N/D')}")
    st.write(f"**Devise :** {currency}")
    st.write(f"**Exchange :** {info.get('exchange','N/D')}")
    st.write(f"**Fuseau marché :** {info.get('exchangeTimezoneName','N/D')}")

    if live_data:
        st.write(f"**Prix live :** {price_line(live_data.get('price'), currency)}")
        st.write(f"**Variation 24h :** {safe_number(live_data.get('change_pct'), 2, '%')}")
        if live_data.get("high"):
            st.write(f"**Haut 24h :** {price_line(live_data.get('high'), currency)}")
        if live_data.get("low"):
            st.write(f"**Bas 24h :** {price_line(live_data.get('low'), currency)}")
        if live_data.get("volume"):
            st.write(f"**Volume 24h :** {money(live_data.get('volume'))}")
        if live_data.get("market_cap"):
            st.write(f"**Market Cap live :** {money(live_data.get('market_cap'))}")
    else:
        st.write(f"**Volume :** {format_int(info.get('volume'))}")
        st.write(f"**Volume moyen :** {format_int(info.get('averageVolume'))}")
        st.write(f"**Ouverture :** {price_line(info.get('open'), currency)}")
        st.write(f"**Plus haut jour :** {price_line(info.get('dayHigh'), currency)}")
        st.write(f"**Plus bas jour :** {price_line(info.get('dayLow'), currency)}")

    st.write(f"**52 sem. haut/bas :** {price_line(info.get('fiftyTwoWeekHigh'), currency)} / {price_line(info.get('fiftyTwoWeekLow'), currency)}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- TAB 2 — PERFORMANCE ----
with tabs[2]:
    st.subheader("📈 Performance holographique")

    period_choice = st.radio(
        "Période",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        horizontal=True,
        index=2,
        label_visibility="collapsed"
    )

    hist_p = get_history(symbol, period_choice)

    if not hist_p.empty and {"Open","High","Low","Close"}.issubset(hist_p.columns):
        close_p = get_close_series(hist_p)

        fig = go.Figure()

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=hist_p.index,
            open=hist_p["Open"].squeeze(),
            high=hist_p["High"].squeeze(),
            low=hist_p["Low"].squeeze(),
            close=hist_p["Close"].squeeze(),
            increasing_line_color="#22d3ee",
            decreasing_line_color="#fb365c",
            increasing_fillcolor="rgba(34,211,238,.25)",
            decreasing_fillcolor="rgba(251,54,92,.25)",
            name="Prix"
        ))

        # MA20
        if len(close_p) >= 20:
            fig.add_trace(go.Scatter(
                x=hist_p.index,
                y=close_p.rolling(20).mean(),
                mode="lines",
                line=dict(color="rgba(168,85,247,.8)", width=1.5),
                name="MA 20"
            ))

        # MA50
        if len(close_p) >= 50:
            fig.add_trace(go.Scatter(
                x=hist_p.index,
                y=close_p.rolling(50).mean(),
                mode="lines",
                line=dict(color="rgba(244,114,182,.8)", width=1.5),
                name="MA 50"
            ))

        # Bollinger Bands
        if len(close_p) >= 20:
            ma = close_p.rolling(20).mean()
            std = close_p.rolling(20).std()
            fig.add_trace(go.Scatter(
                x=hist_p.index, y=ma + 2*std,
                mode="lines",
                line=dict(color="rgba(251,179,0,.3)", width=1, dash="dash"),
                showlegend=False, name="BB+"
            ))
            fig.add_trace(go.Scatter(
                x=hist_p.index, y=ma - 2*std,
                mode="lines",
                line=dict(color="rgba(251,179,0,.3)", width=1, dash="dash"),
                fill="tonexty",
                fillcolor="rgba(251,179,0,.04)",
                showlegend=False, name="BB-"
            ))

        # Volume
        if "Volume" in hist_p.columns:
            fig.add_trace(go.Bar(
                x=hist_p.index,
                y=hist_p["Volume"].squeeze(),
                name="Volume",
                marker_color="rgba(34,211,238,.12)",
                yaxis="y2"
            ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(2,6,23,.85)",
            height=580,
            xaxis_rangeslider_visible=False,
            dragmode=False,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="rgba(34,211,238,.7)")),
            xaxis=dict(showgrid=True, gridcolor="rgba(34,211,238,.06)", fixedrange=True),
            yaxis=dict(showgrid=True, gridcolor="rgba(34,211,238,.06)", fixedrange=True, side="right"),
            yaxis2=dict(overlaying="y", side="left", showgrid=False, fixedrange=True),
            margin=dict(l=0, r=60, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True, config=TOUCH_STABLE_PLOTLY_CONFIG)

        perf = ((close_p.iloc[-1] - close_p.iloc[0]) / close_p.iloc[0] * 100) if close_p.iloc[0] else 0
        st.markdown(
            f'<span class="mini-chip">Performance : {perf:.2f}%</span>'
            f'<span class="mini-chip">Points : {len(close_p)}</span>',
            unsafe_allow_html=True
        )
    else:
        unavailable_box("Graphique temporairement indisponible")

# ---- TAB 3 — RATIOS ----
with tabs[3]:
    st.subheader("📊 Ratios Financiers")
    cols = st.columns(3)
    ratios = [
        ("P/E Ratio", safe_number(info.get("trailingPE"), 2)),
        ("Forward P/E", safe_number(info.get("forwardPE"), 2)),
        ("PEG Ratio", safe_number(info.get("pegRatio"), 2)),
        ("P/B Ratio", safe_number(info.get("priceToBook"), 2)),
        ("P/S Ratio", safe_number(info.get("priceToSalesTrailing12Months"), 2)),
        ("EV/EBITDA", safe_number(info.get("enterpriseToEbitda"), 2)),
        ("Dividend Yield", safe_number((info.get("dividendYield") or 0)*100, 2, "%")),
        ("Payout Ratio", safe_number(info.get("payoutRatio"), 2)),
        ("ROE", safe_number((info.get("returnOnEquity") or 0)*100, 2, "%")),
        ("ROA", safe_number((info.get("returnOnAssets") or 0)*100, 2, "%")),
        ("Profit Margin", safe_number((info.get("profitMargins") or 0)*100, 2, "%")),
        ("Debt/Equity", safe_number(info.get("debtToEquity"), 2)),
    ]
    for i, (label, val) in enumerate(ratios):
        cols[i % 3].markdown(
            f'<div class="kpi" style="margin-bottom:12px">'
            f'<div class="kpi-title">{label}</div>'
            f'<div class="kpi-value" style="font-size:20px">{val}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(f"**Chiffre d'affaires :** {money(info.get('totalRevenue'))}")
    st.write(f"**EBITDA :** {money(info.get('ebitda'))}")
    st.write(f"**Cash total :** {money(info.get('totalCash'))}")
    st.write(f"**Dette totale :** {money(info.get('totalDebt'))}")
    st.write(f"**Recommandation :** {info.get('recommendationKey','N/D')}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- TAB 4 — RISQUE ----
with tabs[4]:
    st.subheader("⚠️ Analyse de Risque")
    if data_available and len(close) >= 3:
        returns = close.pct_change().dropna()
        volatility = returns.std() * (252**0.5) * 100
        drawdown = ((close / close.cummax()) - 1).min() * 100
        sharpe = (returns.mean() / returns.std()) * (252**0.5) if returns.std() > 0 else 0
        downside = returns[returns < 0].std() * (252**0.5) * 100 if not returns[returns < 0].empty else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Volatilité", f"{volatility:.1f}%")
        c2.metric("Perte max", f"{drawdown:.1f}%")
        c3.metric("Sharpe", f"{sharpe:.2f}")
        c4.metric("Vol. baissière", f"{downside:.1f}%")

        risk = "élevé" if volatility >= 55 or drawdown <= -35 else "modéré" if volatility >= 30 or drawdown <= -18 else "faible"
        st.markdown(
            f'<div class="notice">Niveau de risque détecté : <strong>{risk}</strong>. '
            'Aucun rendement garanti.</div>',
            unsafe_allow_html=True
        )

        # Drawdown chart
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=close.index,
            y=((close / close.cummax()) - 1) * 100,
            fill="tozeroy",
            mode="lines",
            line=dict(color="#fb365c", width=1.5),
            fillcolor="rgba(251,54,92,.15)",
            name="Drawdown %"
        ))
        fig_dd.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(2,6,23,.85)",
            height=300,
            margin=dict(l=0,r=0,t=20,b=0),
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        st.plotly_chart(fig_dd, use_container_width=True, config=TOUCH_STABLE_PLOTLY_CONFIG)
    else:
        unavailable_box("Module risque indisponible")

# ---- TAB 5 — RÉSUMÉ ----
with tabs[5]:
    st.subheader("🧠 Résumé IA local")
    if data_available and price:
        ma20 = close.tail(20).mean()
        ma60 = close.tail(60).mean() if len(close) >= 60 else ma20
        perf = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100) if close.iloc[0] else 0
        volatility = close.pct_change().std() * (252**0.5) * 100

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = float((100 - (100 / (1 + rs))).iloc[-1]) if not rs.empty else 50

        score = 0
        signals = []

        if price > ma20:
            score += 1
            signals.append(("✅", f"Prix ({price:.2f}) > MA20 ({ma20:.2f})", "good"))
        else:
            signals.append(("⚠️", f"Prix ({price:.2f}) < MA20 ({ma20:.2f})", "bad"))

        if price > ma60:
            score += 1
            signals.append(("✅", f"Prix > MA60 ({ma60:.2f})", "good"))
        else:
            signals.append(("⚠️", f"Prix < MA60 ({ma60:.2f})", "bad"))

        if perf > 5:
            score += 1
            signals.append(("✅", f"Performance 6 mois : +{perf:.1f}%", "good"))
        else:
            signals.append(("⚠️", f"Performance 6 mois : {perf:.1f}%", "bad"))

        if volatility < 35:
            score += 1
            signals.append(("✅", f"Volatilité maîtrisée : {volatility:.1f}%", "good"))
        else:
            signals.append(("⚠️", f"Forte volatilité : {volatility:.1f}%", "bad"))

        if 30 < rsi < 70:
            score += 1
            signals.append(("✅", f"RSI neutre : {rsi:.0f}", "good"))
        elif rsi <= 30:
            signals.append(("🔵", f"RSI survendu : {rsi:.0f} — possible rebond", "neutral"))
        else:
            signals.append(("🔴", f"RSI suracheté : {rsi:.0f} — prudence", "bad"))

        verdict = "TENDANCE POSITIVE" if score >= 4 else "SIGNAL NEUTRE" if score >= 2 else "SIGNAL NÉGATIF"
        vcolor = "#00ff41" if score >= 4 else "#ffb300" if score >= 2 else "#fb365c"

        st.markdown(
            f'<div class="card">'
            f'<div style="font-family:Courier New,monospace;font-size:20px;color:{vcolor};'
            f'text-shadow:0 0 12px {vcolor};margin-bottom:10px">VERDICT : {verdict}</div>'
            f'<div style="color:rgba(255,255,255,.6);font-size:13px">Score : <strong style="color:{vcolor}">{score}/5</strong></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        for icon, text, tone in signals:
            color = "#00ff41" if tone == "good" else "#fb365c" if tone == "bad" else "#ffb300"
            st.markdown(
                f'<div style="padding:8px 14px;margin:4px 0;border-left:2px solid {color};'
                f'background:rgba(0,0,0,.3);border-radius:0 8px 8px 0;font-size:13px;color:{color}">'
                f'{icon} {text}</div>',
                unsafe_allow_html=True
            )

        st.warning("⚠️ Analyse éducative uniquement. Pas de conseil financier. Risque de perte en capital.")
    else:
        unavailable_box("Résumé indisponible")

# ---- TAB 6 — HEATMAP ----
with tabs[6]:
    st.subheader("🔥 Heatmap Néon")

    hm_choice = st.radio(
        "Catégorie heatmap",
        ["Tech US", "Crypto Top 20", "Europe CAC", "Indices mondiaux", "Matières premières"],
        horizontal=True
    )

    hm_map = {
        "Tech US": [
            ("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","Nvidia"),
            ("GOOGL","Google"),("META","Meta"),("AMZN","Amazon"),
            ("TSLA","Tesla"),("AMD","AMD"),("AVGO","Broadcom"),
            ("ORCL","Oracle"),("CRM","Salesforce"),("ADBE","Adobe"),
        ],
        "Crypto Top 20": [
            ("BTC-USD","Bitcoin"),("ETH-USD","Ethereum"),("BNB-USD","BNB"),
            ("SOL-USD","Solana"),("XRP-USD","XRP"),("DOGE-USD","Dogecoin"),
            ("ADA-USD","Cardano"),("AVAX-USD","Avalanche"),("LINK-USD","Chainlink"),
            ("DOT-USD","Polkadot"),("MATIC-USD","Polygon"),("LTC-USD","Litecoin"),
            ("ATOM-USD","Cosmos"),("UNI-USD","Uniswap"),("APT-USD","Aptos"),
            ("ARB-USD","Arbitrum"),("OP-USD","Optimism"),("INJ-USD","Injective"),
            ("SUI-USD","Sui"),("NEAR-USD","Near"),
        ],
        "Europe CAC": [
            ("MC.PA","LVMH"),("RMS.PA","Hermès"),("AIR.PA","Airbus"),
            ("TTE.PA","TotalEnergies"),("SU.PA","Schneider"),("OR.PA","L'Oréal"),
            ("SAN.PA","Sanofi"),("BNP.PA","BNP"),("SAF.PA","Safran"),
            ("DSY.PA","Dassault"),("KER.PA","Kering"),("CS.PA","AXA"),
        ],
        "Indices mondiaux": [
            ("^GSPC","S&P500"),("^NDX","Nasdaq100"),("^DJI","DowJones"),
            ("^FCHI","CAC40"),("^GDAXI","DAX"),("^FTSE","FTSE100"),
            ("^N225","Nikkei"),("^HSI","HangSeng"),("^STOXX50E","EuroStoxx"),
            ("^RUT","Russell2000"),("^AXJO","ASX200"),("^BSESN","Sensex"),
        ],
        "Matières premières": [
            ("GC=F","Or"),("SI=F","Argent"),("CL=F","Oil WTI"),
            ("BZ=F","Brent"),("NG=F","Gaz"),("HG=F","Cuivre"),
            ("ZC=F","Maïs"),("ZW=F","Blé"),("PL=F","Platine"),
        ],
    }

    perf_rows = []
    with st.spinner("Chargement heatmap..."):
        for sym, label in hm_map.get(hm_choice, []):
            try:
                h = get_history(sym, "1mo")
                c = get_close_series(h)
                if len(c) >= 2 and c.iloc[0]:
                    p = float((c.iloc[-1] - c.iloc[0]) / c.iloc[0] * 100)
                    perf_rows.append({"label": label, "symbol": sym, "perf": round(p, 2)})
            except Exception:
                pass

    if perf_rows:
        dfp = pd.DataFrame(perf_rows)
        fig_hm = px.treemap(
            dfp,
            path=["label"],
            values=dfp["perf"].abs() + 1,
            color="perf",
            color_continuous_scale=[
                [0,"#fb365c"],[0.3,"#4a0000"],
                [0.5,"#0a0f1e"],[0.7,"#003320"],
                [1,"#00ff41"]
            ],
            color_continuous_midpoint=0,
            hover_data={"perf":":.2f"}
        )
        fig_hm.update_traces(
            textfont=dict(family="Courier New", size=13, color="white"),
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.2f}%"
        )
        fig_hm.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=520,
            margin=dict(l=0,r=0,t=20,b=0)
        )
        st.plotly_chart(fig_hm, use_container_width=True, config=TOUCH_STABLE_PLOTLY_CONFIG)
    else:
        unavailable_box("Heatmap temporairement indisponible")

# ---- TAB 7 — TRADINGVIEW ----
with tabs[7]:
    st.subheader("🌐 TradingView Live")
    st.markdown(
        '<div class="notice">Graphique TradingView intégré pour visualisation complémentaire.</div>',
        unsafe_allow_html=True
    )
    url = f"https://s.tradingview.com/widgetembed/?symbol={tv_symbol(symbol)}&interval=D&theme=dark&style=1&locale=fr"
    components.iframe(url, height=620, scrolling=False)

# ---- TAB 8 — WATCHLIST ----
with tabs[8]:
    st.subheader("⭐ Watchlist")

    col_add, col_clear = st.columns([3, 1])
    with col_add:
        if st.button(f"➕ Ajouter {symbol}"):
            if symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(symbol)
                st.toast(f"✅ {symbol} ajouté", icon="⭐")
            else:
                st.toast(f"Déjà dans la watchlist", icon="☑️")
    with col_clear:
        if st.button("🗑️ Vider"):
            st.session_state.watchlist = []

    if st.session_state.watchlist:
        wl_rows = []
        for ws in st.session_state.watchlist:
            try:
                wh = get_history(ws, "5d")
                wc = get_close_series(wh)
                if len(wc) >= 2:
                    wp = float(wc.iloc[-1])
                    wch = ((wc.iloc[-1]-wc.iloc[-2])/wc.iloc[-2]*100) if wc.iloc[-2] else 0
                    wl_rows.append({
                        "Symbole": ws,
                        "Prix": f"{wp:,.2f}",
                        "Variation": f"{'▲' if wch >= 0 else '▼'} {abs(wch):.2f}%",
                        "Signal": "🟢 BULL" if wch >= 0 else "🔴 BEAR"
                    })
                else:
                    wl_rows.append({"Symbole": ws, "Prix": "N/D", "Variation": "N/D", "Signal": "—"})
            except Exception:
                wl_rows.append({"Symbole": ws, "Prix": "N/D", "Variation": "N/D", "Signal": "—"})

        st.dataframe(pd.DataFrame(wl_rows), use_container_width=True, hide_index=True)
    else:
        st.markdown(
            '<div class="data-missing">Watchlist vide. Ajoutez un actif pour commencer.</div>',
            unsafe_allow_html=True
        )

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    '<div class="footer">Stock Insight Neon Terminal — '
    'Finnhub + CoinGecko + Yahoo Finance — Sans API payante — '
    'Pas de conseil financier — Risque de perte en capital</div>',
    unsafe_allow_html=True
)
