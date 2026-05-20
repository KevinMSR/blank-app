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


TOUCH_STABLE_PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "doubleClick": False,
    "responsive": True,
}


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


def render_analysis_audio_layer(asset_name, symbol):
    """Injects a browser-local cyberpunk analysis ambience and voice layer."""
    audio_html = (
        """
<div id="stock-insight-analysis-audio-root"></div>
<script>
(function () {
  "use strict";

  const CONFIG = {
    assetName: __ASSET_NAME__,
    symbol: __SYMBOL__
  };
  const ROOT_KEY = "__stockInsightAnalysisAudio";
  const PANEL_ID = "stock-insight-audio-panel";
  const TOGGLE_ID = "stock-insight-audio-toggle";
  const VOLUME_ID = "stock-insight-audio-volume";
  const VOLUME_LABEL_ID = "stock-insight-audio-volume-label";
  const STYLE_ID = "stock-insight-audio-style";
  const VOLUME_LEVELS = ["low", "medium", "high"];
  const VOLUME_LABELS = { low: "faible", medium: "moyen", high: "fort" };
  const VOLUME_GAINS = { low: 0.58, medium: 0.86, high: 1.14 };

  function getParentWindow() {
    try {
      if (window.parent) return window.parent;
    } catch (e) {}
    return window;
  }

  function getDoc(rootWindow) {
    try {
      if (rootWindow && rootWindow.document) return rootWindow.document;
    } catch (e) {}
    return document;
  }

  let rootWindow = getParentWindow();
  let doc = getDoc(rootWindow);
  let existingState;
  let STATE;
  try {
    existingState = rootWindow[ROOT_KEY] || {};
    rootWindow[ROOT_KEY] = existingState;
    STATE = existingState;
  } catch (e) {
    rootWindow = window;
    doc = document;
    existingState = window[ROOT_KEY] || {};
    window[ROOT_KEY] = existingState;
    STATE = existingState;
  }

  STATE.assetName = String(CONFIG.assetName || CONFIG.symbol || "selected asset").trim();
  STATE.symbol = String(CONFIG.symbol || "").trim();
  STATE.boundButtons = STATE.boundButtons || new WeakSet();
  STATE.ctx = STATE.ctx || null;
  STATE.ambient = STATE.ambient || null;
  STATE.started = STATE.started || false;
  STATE.storageLoaded = STATE.storageLoaded || false;
  STATE.volumeLevel = STATE.volumeLevel || "medium";

  function loadAmbientPreference() {
    try {
      const saved = rootWindow.localStorage.getItem("stockInsightAmbientEnabled");
      return saved === null ? true : saved === "true";
    } catch (e) {
      return true;
    }
  }

  function saveAmbientPreference() {
    try {
      rootWindow.localStorage.setItem("stockInsightAmbientEnabled", STATE.enabled ? "true" : "false");
    } catch (e) {}
  }

  function loadVolumePreference() {
    try {
      const saved = rootWindow.localStorage.getItem("stockInsightAmbientVolume");
      return VOLUME_LEVELS.includes(saved) ? saved : "medium";
    } catch (e) {
      return "medium";
    }
  }

  function saveVolumePreference() {
    try {
      rootWindow.localStorage.setItem("stockInsightAmbientVolume", STATE.volumeLevel);
    } catch (e) {}
  }

  if (!STATE.storageLoaded) {
    STATE.enabled = loadAmbientPreference();
    STATE.volumeLevel = loadVolumePreference();
    STATE.storageLoaded = true;
  } else if (typeof STATE.enabled !== "boolean") {
    STATE.enabled = true;
  }

  if (!VOLUME_LEVELS.includes(STATE.volumeLevel)) {
    STATE.volumeLevel = "medium";
  }

  function volumeMultiplier() {
    return VOLUME_GAINS[STATE.volumeLevel] || VOLUME_GAINS.medium;
  }

  function masterTargetGain() {
    return 0.042 * volumeMultiplier();
  }

  function applyVolume(seconds) {
    if (!STATE.ambient || !STATE.ctx) return;
    const ctx = STATE.ctx;
    const now = ctx.currentTime;
    const ramp = typeof seconds === "number" ? seconds : 0.28;
    try {
      STATE.ambient.master.gain.cancelScheduledValues(now);
      STATE.ambient.master.gain.setValueAtTime(Math.max(STATE.ambient.master.gain.value, 0.0001), now);
      STATE.ambient.master.gain.linearRampToValueAtTime(masterTargetGain(), now + ramp);
    } catch (e) {}
  }

  function audioConstructor() {
    return rootWindow.AudioContext || rootWindow.webkitAudioContext || window.AudioContext || window.webkitAudioContext;
  }

  function ensureAudio() {
    const AudioContext = audioConstructor();
    if (!AudioContext) return null;
    if (!STATE.ctx || STATE.ctx.state === "closed") {
      STATE.ctx = new AudioContext();
    }
    if (STATE.ctx.state === "suspended") {
      try {
        const resumeResult = STATE.ctx.resume();
        if (resumeResult && resumeResult.catch) resumeResult.catch(function () {});
      } catch (e) {}
    }
    STATE.started = true;
    return STATE.ctx;
  }

  function makeOsc(type, frequency, gainValue, destination) {
    const ctx = STATE.ctx;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(frequency, ctx.currentTime);
    gain.gain.setValueAtTime(gainValue, ctx.currentTime);
    osc.connect(gain);
    gain.connect(destination);
    osc.start();
    return { osc: osc, gain: gain };
  }

  function makeNoise(seconds) {
    const ctx = STATE.ctx;
    const length = Math.max(1, Math.floor(ctx.sampleRate * seconds));
    const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < length; i += 1) {
      data[i] = (Math.random() * 2 - 1) * 0.42;
    }
    return buffer;
  }

  function makeMetallicImpulse(seconds) {
    const ctx = STATE.ctx;
    const length = Math.max(1, Math.floor(ctx.sampleRate * seconds));
    const buffer = ctx.createBuffer(2, length, ctx.sampleRate);
    for (let channel = 0; channel < 2; channel += 1) {
      const data = buffer.getChannelData(channel);
      for (let i = 0; i < length; i += 1) {
        const t = i / ctx.sampleRate;
        const decay = Math.pow(1 - i / length, 2.6);
        const ring = Math.sin(t * 880 * Math.PI * 2) * 0.34 + Math.sin(t * 1327 * Math.PI * 2) * 0.22;
        data[i] = ((Math.random() * 2 - 1) * 0.42 + ring) * decay * 0.28;
      }
    }
    return buffer;
  }

  function createPan(value) {
    const ctx = STATE.ctx;
    if (ctx.createStereoPanner) {
      const panner = ctx.createStereoPanner();
      panner.pan.setValueAtTime(value, ctx.currentTime);
      return panner;
    }
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(1, ctx.currentTime);
    return gain;
  }

  function startAmbience() {
    const ctx = ensureAudio();
    if (!ctx || !STATE.enabled || STATE.ambient) return;

    const now = ctx.currentTime;
    const tempo = 76;
    const beat = 60 / tempo;
    const bar = beat * 4;
    const cycle = bar * 2;
    const master = ctx.createGain();
    const compressor = ctx.createDynamicsCompressor();
    const ambienceBus = ctx.createGain();
    const bassGain = ctx.createGain();
    const rhythmBus = ctx.createGain();
    const padBus = ctx.createGain();
    const textureBus = ctx.createGain();
    const effectsInput = ctx.createGain();
    const reverbSend = ctx.createGain();
    const convolver = ctx.createConvolver();
    const reverbFilter = ctx.createBiquadFilter();
    const reverbGain = ctx.createGain();
    const delaySend = ctx.createGain();
    const delay = ctx.createDelay(2.4);
    const delayFilter = ctx.createBiquadFilter();
    const delayFeedback = ctx.createGain();
    const delayGain = ctx.createGain();
    const nodes = [];
    const timers = [];

    master.gain.setValueAtTime(0.0001, now);
    master.gain.linearRampToValueAtTime(masterTargetGain(), now + 2.4);
    ambienceBus.gain.setValueAtTime(0.82, now);
    bassGain.gain.setValueAtTime(0.96, now);
    rhythmBus.gain.setValueAtTime(0.64, now);
    padBus.gain.setValueAtTime(0.50, now);
    textureBus.gain.setValueAtTime(0.36, now);
    effectsInput.gain.setValueAtTime(0.78, now);
    reverbSend.gain.setValueAtTime(0.13, now);
    reverbGain.gain.setValueAtTime(0.20, now);
    delaySend.gain.setValueAtTime(0.18, now);
    delay.delayTime.setValueAtTime(beat * 0.75, now);
    delayFeedback.gain.setValueAtTime(0.24, now);
    delayGain.gain.setValueAtTime(0.17, now);

    compressor.threshold.setValueAtTime(-25, now);
    compressor.knee.setValueAtTime(16, now);
    compressor.ratio.setValueAtTime(3.4, now);
    compressor.attack.setValueAtTime(0.018, now);
    compressor.release.setValueAtTime(0.46, now);
    convolver.buffer = makeMetallicImpulse(1.9);
    reverbFilter.type = "bandpass";
    reverbFilter.frequency.setValueAtTime(720, now);
    reverbFilter.Q.setValueAtTime(1.25, now);
    delayFilter.type = "lowpass";
    delayFilter.frequency.setValueAtTime(1280, now);
    delayFilter.Q.setValueAtTime(0.8, now);

    bassGain.connect(ambienceBus);
    rhythmBus.connect(ambienceBus);
    padBus.connect(ambienceBus);
    textureBus.connect(ambienceBus);
    ambienceBus.connect(compressor);
    ambienceBus.connect(reverbSend);
    padBus.connect(delaySend);
    textureBus.connect(delaySend);
    effectsInput.connect(compressor);
    effectsInput.connect(reverbSend);
    effectsInput.connect(delaySend);
    delaySend.connect(delay);
    delay.connect(delayFilter);
    delayFilter.connect(delayFeedback);
    delayFeedback.connect(delay);
    delayFilter.connect(delayGain);
    delayGain.connect(compressor);
    reverbSend.connect(convolver);
    convolver.connect(reverbFilter);
    reverbFilter.connect(reverbGain);
    reverbGain.connect(compressor);
    compressor.connect(master);
    master.connect(ctx.destination);

    function rememberInterval(handler, milliseconds) {
      const id = rootWindow.setInterval(handler, milliseconds);
      timers.push({ type: "interval", id: id });
      return id;
    }

    function rememberTimeout(handler, milliseconds) {
      const id = rootWindow.setTimeout(handler, milliseconds);
      timers.push({ type: "timeout", id: id });
      return id;
    }

    function env(gainParam, start, peak, attack, hold, release) {
      const safePeak = Math.max(0.0002, peak);
      gainParam.cancelScheduledValues(start);
      gainParam.setValueAtTime(0.0001, start);
      gainParam.linearRampToValueAtTime(safePeak, start + attack);
      gainParam.setValueAtTime(safePeak * 0.82, start + attack + hold);
      gainParam.exponentialRampToValueAtTime(0.0001, start + attack + hold + release);
    }

    function connectPanned(node, panValue, destination) {
      const pan = createPan(panValue);
      node.connect(pan);
      pan.connect(destination);
      return pan;
    }

    function stopSource(source, stopAt) {
      try {
        source.stop(stopAt);
      } catch (e) {}
    }

    function scheduleBass(note, start, length, velocity) {
      const sub = ctx.createOscillator();
      const body = ctx.createOscillator();
      const subGain = ctx.createGain();
      const bodyGain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      const amp = ctx.createGain();
      sub.type = "sine";
      body.type = "sawtooth";
      sub.frequency.setValueAtTime(note, start);
      body.frequency.setValueAtTime(note * 2.01, start);
      body.detune.setValueAtTime(-6, start);
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(118, start);
      filter.frequency.linearRampToValueAtTime(174, start + 0.08);
      filter.frequency.exponentialRampToValueAtTime(92, start + length + 0.12);
      filter.Q.setValueAtTime(1.2, start);
      subGain.gain.setValueAtTime(0.13 * velocity, start);
      bodyGain.gain.setValueAtTime(0.030 * velocity, start);
      env(amp.gain, start, 1, 0.026, Math.max(0.05, length * 0.42), Math.max(0.18, length * 0.55));
      sub.connect(subGain);
      body.connect(bodyGain);
      subGain.connect(filter);
      bodyGain.connect(filter);
      filter.connect(amp);
      amp.connect(bassGain);
      sub.start(start);
      body.start(start);
      stopSource(sub, start + length + 0.38);
      stopSource(body, start + length + 0.38);
    }

    function scheduleKick(start, strong) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      osc.type = "sine";
      osc.frequency.setValueAtTime(strong ? 52 : 46, start);
      osc.frequency.exponentialRampToValueAtTime(28, start + 0.36);
      filter.type = "lowpass";
      filter.frequency.setValueAtTime(126, start);
      filter.Q.setValueAtTime(0.72, start);
      env(gain.gain, start, strong ? 0.16 : 0.105, 0.012, 0.038, 0.38);
      osc.connect(filter);
      filter.connect(gain);
      gain.connect(rhythmBus);
      osc.start(start);
      stopSource(osc, start + 0.54);
    }

    function scheduleTacticalClick(start, panValue, accent) {
      const noise = ctx.createBufferSource();
      const toneOsc = ctx.createOscillator();
      const noiseGain = ctx.createGain();
      const toneGain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      const sum = ctx.createGain();
      noise.buffer = makeNoise(0.16);
      toneOsc.type = "triangle";
      toneOsc.frequency.setValueAtTime(accent ? 1180 : 760, start);
      toneOsc.frequency.exponentialRampToValueAtTime(accent ? 520 : 430, start + 0.09);
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(accent ? 1850 : 1380, start);
      filter.Q.setValueAtTime(7.5, start);
      env(noiseGain.gain, start, accent ? 0.016 : 0.010, 0.006, 0.018, 0.075);
      env(toneGain.gain, start, accent ? 0.018 : 0.012, 0.006, 0.022, 0.11);
      noise.connect(filter);
      filter.connect(noiseGain);
      toneOsc.connect(toneGain);
      noiseGain.connect(sum);
      toneGain.connect(sum);
      connectPanned(sum, panValue, rhythmBus);
      noise.start(start);
      toneOsc.start(start);
      stopSource(noise, start + 0.18);
      stopSource(toneOsc, start + 0.18);
    }

    function schedulePadChord(chord, start, chordIndex) {
      const duration = cycle + 1.65;
      chord.forEach(function (note, index) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const filter = ctx.createBiquadFilter();
        const panValue = [-0.42, 0.38, -0.12, 0.18, 0.48][index % 5];
        osc.type = index % 2 ? "triangle" : "sawtooth";
        osc.frequency.setValueAtTime(note, start);
        osc.detune.setValueAtTime((index - 1.5) * 5 + (chordIndex % 2 ? 3 : -2), start);
        filter.type = "lowpass";
        filter.frequency.setValueAtTime(360 + chordIndex * 34 + index * 24, start);
        filter.frequency.linearRampToValueAtTime(650 + index * 38, start + duration * 0.42);
        filter.frequency.exponentialRampToValueAtTime(390 + index * 30, start + duration - 0.2);
        filter.Q.setValueAtTime(0.9, start);
        gain.gain.setValueAtTime(0.0001, start);
        gain.gain.linearRampToValueAtTime(0.010 - index * 0.0009, start + 1.45 + index * 0.18);
        gain.gain.linearRampToValueAtTime(0.0065 - index * 0.00055, start + duration * 0.68);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        osc.connect(filter);
        filter.connect(gain);
        connectPanned(gain, panValue, padBus);
        osc.start(start);
        stopSource(osc, start + duration + 0.08);
      });
    }

    function scheduleTechAccent(freq, start, panValue, length, gainValue) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      osc.type = "square";
      osc.frequency.setValueAtTime(freq, start);
      osc.frequency.exponentialRampToValueAtTime(freq * 0.74, start + length);
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(freq * 1.55, start);
      filter.Q.setValueAtTime(8.5, start);
      env(gain.gain, start, gainValue, 0.012, length * 0.18, length * 0.82);
      osc.connect(filter);
      filter.connect(gain);
      connectPanned(gain, panValue, textureBus);
      osc.start(start);
      stopSource(osc, start + length + 0.05);
    }

    function scheduleTransition(start, cycleIndex) {
      const sweep = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      const pan = createPan(cycleIndex % 2 ? -0.32 : 0.32);
      sweep.type = "sawtooth";
      sweep.frequency.setValueAtTime(96, start);
      sweep.frequency.exponentialRampToValueAtTime(410, start + 1.05);
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(260, start);
      filter.frequency.linearRampToValueAtTime(920, start + 1.05);
      filter.Q.setValueAtTime(6.2, start);
      env(gain.gain, start, 0.024, 0.08, 0.35, 0.72);
      sweep.connect(filter);
      filter.connect(gain);
      gain.connect(pan);
      pan.connect(textureBus);
      sweep.start(start);
      stopSource(sweep, start + 1.2);
    }

    const padPulse = ctx.createOscillator();
    const padPulseDepth = ctx.createGain();
    padPulse.type = "sine";
    padPulse.frequency.setValueAtTime(0.031, now);
    padPulseDepth.gain.setValueAtTime(0.055, now);
    padPulse.connect(padPulseDepth);
    padPulseDepth.connect(padBus.gain);
    padPulse.start();
    nodes.push({ osc: padPulse, gain: padPulseDepth });

    const tensionOsc = ctx.createOscillator();
    const tensionGain = ctx.createGain();
    const tensionFilter = ctx.createBiquadFilter();
    tensionOsc.type = "sawtooth";
    tensionOsc.frequency.setValueAtTime(58, now);
    tensionFilter.type = "bandpass";
    tensionFilter.frequency.setValueAtTime(360, now);
    tensionFilter.Q.setValueAtTime(4.4, now);
    tensionGain.gain.setValueAtTime(0.0001, now);
    tensionOsc.connect(tensionFilter);
    tensionFilter.connect(tensionGain);
    tensionGain.connect(textureBus);
    tensionOsc.start();
    nodes.push({ osc: tensionOsc, gain: tensionGain });

    const chordProgression = [
      [87.31, 130.81, 174.61, 261.63],
      [69.30, 103.83, 138.59, 207.65],
      [77.78, 116.54, 155.56, 233.08],
      [65.41, 98.00, 130.81, 196.00]
    ];
    const bassPattern = [
      { beat: 0, note: 43.65, length: 0.78, velocity: 1.00 },
      { beat: 1.5, note: 43.65, length: 0.42, velocity: 0.64 },
      { beat: 2.5, note: 51.91, length: 0.52, velocity: 0.72 },
      { beat: 3.5, note: 58.27, length: 0.44, velocity: 0.58 },
      { beat: 4, note: 38.89, length: 0.82, velocity: 0.94 },
      { beat: 5.5, note: 43.65, length: 0.45, velocity: 0.66 },
      { beat: 6, note: 51.91, length: 0.58, velocity: 0.72 },
      { beat: 7.25, note: 65.41, length: 0.38, velocity: 0.54 }
    ];
    const accents = [
      { beat: 0.75, freq: 523.25, pan: -0.48 },
      { beat: 2.25, freq: 392.00, pan: 0.36 },
      { beat: 3.75, freq: 466.16, pan: -0.18 },
      { beat: 5.25, freq: 622.25, pan: 0.46 },
      { beat: 6.75, freq: 349.23, pan: -0.36 }
    ];
    let cycleIndex = 0;

    function scheduleCycle() {
      if (!STATE.ambient || !STATE.enabled || !STATE.ctx) return;
      const start = ctx.currentTime + 0.08;
      const chord = chordProgression[cycleIndex % chordProgression.length];
      schedulePadChord(chord, start, cycleIndex);
      bassPattern.forEach(function (step) {
        scheduleBass(step.note, start + step.beat * beat, step.length * beat, step.velocity);
      });
      [0, 2, 4, 6].forEach(function (beatNumber) {
        scheduleKick(start + beatNumber * beat, beatNumber === 0 || beatNumber === 4);
      });
      [1, 3, 5, 7].forEach(function (beatNumber, index) {
        scheduleTacticalClick(start + beatNumber * beat, index % 2 ? 0.30 : -0.28, beatNumber === 5);
      });
      accents.forEach(function (step, index) {
        const rotate = (index + cycleIndex) % accents.length;
        scheduleTechAccent(
          accents[rotate].freq,
          start + step.beat * beat,
          accents[rotate].pan,
          0.16 + (index % 2) * 0.05,
          0.016 + (index === 3 ? 0.006 : 0)
        );
      });
      if (cycleIndex % 2 === 1) {
        scheduleTransition(start + 7.15 * beat, cycleIndex);
      }
      try {
        textureBus.gain.cancelScheduledValues(start);
        textureBus.gain.setValueAtTime(textureBus.gain.value || 0.36, start);
        textureBus.gain.linearRampToValueAtTime(cycleIndex % 3 === 2 ? 0.44 : 0.34, start + cycle * 0.55);
        textureBus.gain.linearRampToValueAtTime(0.36, start + cycle - 0.1);
      } catch (e) {}
      cycleIndex += 1;
    }

    STATE.ambient = {
      master: master,
      nodes: nodes,
      timers: timers,
      bassGain: bassGain,
      rhythmBus: rhythmBus,
      padBus: padBus,
      textureBus: textureBus,
      tensionGain: tensionGain,
      effectsInput: effectsInput
    };

    scheduleCycle();
    rememberInterval(scheduleCycle, Math.floor(cycle * 1000));
    rememberInterval(function () {
      if (!STATE.ambient || !STATE.enabled || !STATE.ctx) return;
      const modNow = ctx.currentTime;
      try {
        delayFeedback.gain.cancelScheduledValues(modNow);
        delayFeedback.gain.setValueAtTime(delayFeedback.gain.value || 0.24, modNow);
        delayFeedback.gain.linearRampToValueAtTime(0.18 + Math.random() * 0.12, modNow + 3.2);
      } catch (e) {}
      try {
        reverbFilter.frequency.cancelScheduledValues(modNow);
        reverbFilter.frequency.setValueAtTime(reverbFilter.frequency.value || 720, modNow);
        reverbFilter.frequency.linearRampToValueAtTime(620 + Math.random() * 360, modNow + 4.8);
      } catch (e) {}
    }, Math.floor(cycle * 2000));
    rememberTimeout(function () {
      if (STATE.ambient && STATE.enabled) scheduleTransition(ctx.currentTime + 0.1, 0);
    }, 640);

    updateToggleButton();
  }

  function stopAmbience() {
    if (!STATE.ambient || !STATE.ctx) return;
    const ctx = STATE.ctx;
    const now = ctx.currentTime;
    const ambient = STATE.ambient;
    try {
      ambient.master.gain.cancelScheduledValues(now);
      ambient.master.gain.setValueAtTime(Math.max(ambient.master.gain.value, 0.0001), now);
      ambient.master.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);
    } catch (e) {}
    if (ambient.timers) {
      ambient.timers.forEach(function (timer) {
        try {
          if (timer.type === "timeout") {
            rootWindow.clearTimeout(timer.id);
          } else {
            rootWindow.clearInterval(timer.id);
          }
        } catch (e) {}
      });
    }
    ambient.nodes.forEach(function (node) {
      try {
        node.osc.stop(now + 0.52);
      } catch (e) {}
    });
    window.setTimeout(function () {
      try {
        ambient.master.disconnect();
      } catch (e) {}
      ambient.nodes.forEach(function (node) {
        try {
          node.osc.disconnect();
        } catch (e) {}
      });
    }, 620);
    STATE.ambient = null;
    updateToggleButton();
  }

  function connectEffectOutput(node) {
    if (STATE.ambient && STATE.ambient.effectsInput) {
      node.connect(STATE.ambient.effectsInput);
    } else if (STATE.ctx) {
      node.connect(STATE.ctx.destination);
    }
  }

  function boostAmbienceForScan() {
    if (!STATE.ambient || !STATE.ctx) return;
    const ctx = STATE.ctx;
    const now = ctx.currentTime;
    try {
      STATE.ambient.bassGain.gain.cancelScheduledValues(now);
      STATE.ambient.bassGain.gain.setValueAtTime(Math.max(STATE.ambient.bassGain.gain.value, 1), now);
      STATE.ambient.bassGain.gain.linearRampToValueAtTime(1.34, now + 0.16);
      STATE.ambient.bassGain.gain.linearRampToValueAtTime(1.08, now + 2.15);
      STATE.ambient.bassGain.gain.linearRampToValueAtTime(1, now + 3.4);
    } catch (e) {}
    try {
      STATE.ambient.tensionGain.gain.cancelScheduledValues(now);
      STATE.ambient.tensionGain.gain.setValueAtTime(0.0001, now);
      STATE.ambient.tensionGain.gain.exponentialRampToValueAtTime(0.048, now + 0.92);
      STATE.ambient.tensionGain.gain.exponentialRampToValueAtTime(0.0001, now + 3.2);
    } catch (e) {}
  }

  function tone(options) {
    const ctx = ensureAudio();
    if (!ctx) return;
    const now = ctx.currentTime + (options.delay || 0);
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    osc.type = options.type || "sine";
    osc.frequency.setValueAtTime(Math.max(1, options.freq), now);
    if (options.endFreq) {
      osc.frequency.exponentialRampToValueAtTime(Math.max(1, options.endFreq), now + options.duration);
    }
    filter.type = options.filterType || "lowpass";
    filter.frequency.setValueAtTime(options.filterFreq || 480, now);
    filter.Q.setValueAtTime(options.q || 1, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(options.gain || 0.045, now + 0.018);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + options.duration);
    osc.connect(filter);
    filter.connect(gain);
    connectEffectOutput(gain);
    osc.start(now);
    osc.stop(now + options.duration + 0.04);
  }

  function noiseHit(delay, duration, gainValue, filterFreq) {
    const ctx = ensureAudio();
    if (!ctx) return;
    const now = ctx.currentTime + (delay || 0);
    const source = ctx.createBufferSource();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    source.buffer = makeNoise(Math.max(duration, 0.12));
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(filterFreq || 120, now);
    filter.Q.setValueAtTime(5, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(gainValue || 0.055, now + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    source.connect(filter);
    filter.connect(gain);
    connectEffectOutput(gain);
    source.start(now);
    source.stop(now + duration + 0.03);
  }

  function terminalEffect() {
    const freqs = [96, 128, 172, 244, 188, 132, 282, 218];
    freqs.forEach(function (freq, index) {
      tone({
        freq: freq,
        endFreq: freq * 0.96,
        delay: 0.08 + index * 0.055,
        duration: 0.07,
        type: index % 2 ? "square" : "sawtooth",
        gain: 0.018,
        filterType: "bandpass",
        filterFreq: freq * 1.8,
        q: 7
      });
    });
    noiseHit(0.12, 0.42, 0.030, 520);
  }

  function scanImpactAndRise() {
    startAmbience();
    boostAmbienceForScan();
    tone({ freq: 46, endFreq: 24, delay: 0, duration: 0.86, type: "sine", gain: 0.19, filterFreq: 135 });
    tone({ freq: 78, endFreq: 42, delay: 0.018, duration: 0.54, type: "triangle", gain: 0.074, filterFreq: 210 });
    noiseHit(0, 0.32, 0.082, 90);
    tone({ freq: 58, endFreq: 390, delay: 0.14, duration: 1.45, type: "sawtooth", gain: 0.068, filterType: "bandpass", filterFreq: 470, q: 6 });
    tone({ freq: 118, endFreq: 980, delay: 0.30, duration: 1.08, type: "sawtooth", gain: 0.028, filterType: "bandpass", filterFreq: 760, q: 9 });
    terminalEffect();
  }

  function pickVoice(synthWindow) {
    try {
      const voices = synthWindow.speechSynthesis.getVoices() || [];
      if (!voices.length) return null;
      const preferred = ["daniel", "alex", "fred", "google uk english male", "google us english", "microsoft david"];
      for (const token of preferred) {
        const match = voices.find(function (voice) {
          return voice.name && voice.name.toLowerCase().includes(token);
        });
        if (match) return match;
      }
      return voices.find(function (voice) {
        return voice.lang && voice.lang.toLowerCase().startsWith("en");
      }) || voices[0];
    } catch (e) {
      return null;
    }
  }

  function speak(text) {
    const synthWindow = rootWindow.speechSynthesis ? rootWindow : window;
    if (!synthWindow.speechSynthesis || !synthWindow.SpeechSynthesisUtterance) return;
    try {
      synthWindow.speechSynthesis.cancel();
      const utterance = new synthWindow.SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      utterance.rate = 0.68;
      utterance.pitch = 0.36;
      utterance.volume = STATE.volumeLevel === "low" ? 0.74 : 0.88;
      const voice = pickVoice(synthWindow);
      if (voice) utterance.voice = voice;
      synthWindow.speechSynthesis.speak(utterance);
    } catch (e) {}
  }

  function assetName() {
    return (STATE.assetName || STATE.symbol || "selected asset").replace(/\\s+/g, " ").trim();
  }

  function launchAnalysisVoice(mode) {
    const name = assetName();
    if (mode === "launch") {
      speak("Launching " + name + " analysis.");
    } else {
      speak("Analyzing " + name + ".");
    }
  }

  function triggerScan(mode) {
    ensureAudio();
    if (!STATE.enabled) return;
    scanImpactAndRise();
    launchAnalysisVoice(mode);
  }

  function updateToggleButton() {
    const button = doc.getElementById(TOGGLE_ID);
    const volume = doc.getElementById(VOLUME_ID);
    const label = doc.getElementById(VOLUME_LABEL_ID);
    if (button) {
      button.textContent = STATE.enabled ? "Ambiance: ON" : "Ambiance: OFF";
      button.setAttribute("aria-pressed", STATE.enabled ? "true" : "false");
      button.className = STATE.enabled ? "stock-audio-control stock-audio-toggle-on" : "stock-audio-control";
    }
    if (volume) {
      volume.textContent = "Volume: " + (VOLUME_LABELS[STATE.volumeLevel] || VOLUME_LABELS.medium);
      volume.setAttribute("aria-label", "Volume ambiance sonore: " + (VOLUME_LABELS[STATE.volumeLevel] || VOLUME_LABELS.medium));
    }
    if (label) {
      label.textContent = "Audio tactique local";
    }
  }

  function toggleAmbience(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    ensureAudio();
    STATE.enabled = !STATE.enabled;
    saveAmbientPreference();
    if (STATE.enabled) {
      startAmbience();
    } else {
      stopAmbience();
      try {
        (rootWindow.speechSynthesis || window.speechSynthesis).cancel();
      } catch (e) {}
    }
    updateToggleButton();
  }

  function cycleVolume(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    ensureAudio();
    const currentIndex = Math.max(0, VOLUME_LEVELS.indexOf(STATE.volumeLevel));
    STATE.volumeLevel = VOLUME_LEVELS[(currentIndex + 1) % VOLUME_LEVELS.length];
    saveVolumePreference();
    if (STATE.enabled) startAmbience();
    applyVolume(0.22);
    updateToggleButton();
  }

  function installToggle() {
    let style = doc.getElementById(STYLE_ID);
    if (!style) {
      style = doc.createElement("style");
      style.id = STYLE_ID;
      doc.head.appendChild(style);
    }
    style.textContent = [
      ".stock-audio-panel{position:fixed;right:18px;bottom:18px;z-index:2147483000;display:flex;gap:8px;align-items:center;",
      "padding:8px;border-radius:18px;border:1px solid rgba(34,211,238,.32);",
      "background:linear-gradient(135deg,rgba(1,4,12,.96),rgba(15,23,42,.93));",
      "box-shadow:0 0 28px rgba(34,211,238,.16),inset 0 0 22px rgba(15,23,42,.92);backdrop-filter:blur(12px)}",
      ".stock-audio-label{color:#94a3b8;font:800 10px/1 'Courier New',monospace;letter-spacing:.10em;text-transform:uppercase;margin:0 2px;white-space:nowrap}",
      ".stock-audio-control{min-height:42px;padding:10px 12px;border-radius:999px;border:1px solid rgba(34,211,238,.42);",
      "background:linear-gradient(135deg,rgba(3,7,18,.96),rgba(30,41,59,.92));color:#cbd5e1;",
      "font:900 11px/1.1 'Courier New',monospace;letter-spacing:.08em;text-transform:uppercase;",
      "box-shadow:0 0 18px rgba(34,211,238,.12),inset 0 0 14px rgba(15,23,42,.85);",
      "touch-action:manipulation;-webkit-tap-highlight-color:transparent;cursor:pointer}",
      ".stock-audio-control:active{transform:translateY(1px)}",
      ".stock-audio-toggle-on{color:#ecfeff;border-color:rgba(34,211,238,.85);",
      "background:linear-gradient(135deg,rgba(2,6,23,.98),rgba(8,47,73,.92),rgba(88,28,135,.82));",
      "box-shadow:0 0 34px rgba(34,211,238,.38),0 0 52px rgba(88,28,135,.20),inset 0 0 22px rgba(34,211,238,.10)}",
      "@media (max-width:640px){.stock-audio-panel{right:10px;bottom:10px;gap:6px;padding:6px;max-width:calc(100vw - 20px);flex-wrap:wrap}.stock-audio-label{display:none}.stock-audio-control{padding:10px 11px;font-size:10px}}"
    ].join("");

    let panel = doc.getElementById(PANEL_ID);
    if (!panel) {
      panel = doc.createElement("div");
      panel.id = PANEL_ID;
      panel.className = "stock-audio-panel";
      doc.body.appendChild(panel);
    }

    let label = doc.getElementById(VOLUME_LABEL_ID);
    if (!label) {
      label = doc.createElement("span");
      label.id = VOLUME_LABEL_ID;
      label.className = "stock-audio-label";
      panel.appendChild(label);
    }

    let button = doc.getElementById(TOGGLE_ID);
    if (!button) {
      button = doc.createElement("button");
      button.id = TOGGLE_ID;
      button.type = "button";
      button.setAttribute("aria-label", "Activer ou desactiver l'ambiance sonore d'analyse");
      panel.appendChild(button);
    } else if (button.parentNode !== panel) {
      panel.appendChild(button);
    }

    let volume = doc.getElementById(VOLUME_ID);
    if (!volume) {
      volume = doc.createElement("button");
      volume.id = VOLUME_ID;
      volume.type = "button";
      panel.appendChild(volume);
    } else if (volume.parentNode !== panel) {
      panel.appendChild(volume);
    }
    button.onclick = toggleAmbience;
    volume.onclick = cycleVolume;
    updateToggleButton();
  }

  function unlockOnFirstInteraction(event) {
    if (event && event.target && [TOGGLE_ID, VOLUME_ID, PANEL_ID].includes(event.target.id)) return;
    ensureAudio();
    if (STATE.enabled) startAmbience();
  }

  function bindUnlock() {
    if (STATE.unlockHandlers) {
      STATE.unlockHandlers.forEach(function (entry) {
        try {
          entry.doc.removeEventListener(entry.type, entry.handler, true);
        } catch (e) {}
      });
    }
    STATE.unlockHandlers = [];
    ["pointerdown", "touchstart", "keydown", "click"].forEach(function (type) {
      doc.addEventListener(type, unlockOnFirstInteraction, { passive: true, capture: true });
      STATE.unlockHandlers.push({ doc: doc, type: type, handler: unlockOnFirstInteraction });
    });
  }

  function bindScanButtons() {
    const buttons = doc.querySelectorAll("button");
    buttons.forEach(function (button) {
      if ([TOGGLE_ID, VOLUME_ID].includes(button.id) || STATE.boundButtons.has(button)) return;
      STATE.boundButtons.add(button);
      button.addEventListener("click", function () {
        const text = (button.innerText || button.textContent || button.value || button.getAttribute("aria-label") || "").toLowerCase();
        if (text.includes("scanner") || text.includes("scan")) {
          triggerScan("scan");
        } else if (text.includes("lancer la recherche") || text.includes("launch")) {
          triggerScan("launch");
        }
      }, { passive: true });
    });
  }

  if (rootWindow.speechSynthesis) {
    try {
      rootWindow.speechSynthesis.onvoiceschanged = function () {
        pickVoice(rootWindow);
      };
    } catch (e) {}
  }

  installToggle();
  bindUnlock();
  bindScanButtons();
  if (STATE.bindTimer && STATE.bindTimerWindow) {
    try {
      STATE.bindTimerWindow.clearInterval(STATE.bindTimer);
    } catch (e) {}
  }
  STATE.bindTimer = window.setInterval(function () {
    installToggle();
    bindScanButtons();
  }, 900);
  STATE.bindTimerWindow = window;
  if (STATE.started && STATE.enabled && !STATE.ambient) {
    startAmbience();
  }
})();
</script>
"""
        .replace("__ASSET_NAME__", json.dumps(str(asset_name or symbol or "selected asset")))
        .replace("__SYMBOL__", json.dumps(str(symbol or "")))
    )
    components.html(audio_html, height=1)


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


catalog = load_catalog()

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
    name_by_symbol = dict(zip(filtered["symbol"].tolist(), filtered["name"].tolist()))
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
    selected_asset_display_name = name_by_symbol.get(symbol, symbol)
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
    st.caption("Sons : synthèse locale Web Audio, activés après interaction utilisateur")


hist = get_history(symbol)
info = get_info(symbol)
close = get_close_series(hist)
data_available = not close.empty
history_is_fallback = bool(getattr(hist, "attrs", {}).get("is_fallback", False))
selected_asset = ASSET_METADATA.get(symbol, {})

name = info.get("longName") or info.get("shortName") or selected_asset.get("name") or symbol
voice_asset_name = selected_asset_display_name or selected_asset.get("name") or name or symbol
sector = info.get("sector", "N/D")
industry = info.get("industry", "N/D")
country = info.get("country", "N/D")
currency = info.get("currency") or fallback_currency(symbol)
asset_type = info.get("quoteType") or selected_asset.get("category") or "N/D"
price = float(close.iloc[-1]) if data_available else None
previous = float(close.iloc[-2]) if len(close) > 1 else price
change = ((price - previous) / previous) * 100 if price is not None and previous else None


render_analysis_audio_layer(voice_asset_name, symbol)


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
            dragmode=False,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10),
            font=dict(color="#e5e7eb"),
        )
        fig.update_xaxes(
            gridcolor="rgba(34,211,238,.10)",
            fixedrange=True,
            range=[hist.index.min(), hist.index.max()],
        )
        fig.update_yaxes(gridcolor="rgba(34,211,238,.10)", fixedrange=True)
        st.plotly_chart(fig, use_container_width=True, config=TOUCH_STABLE_PLOTLY_CONFIG)

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
    "Ambiance synthétique Web Audio API et voix SpeechSynthesis locales, sans fichier externe.</div>",
    unsafe_allow_html=True,
)
