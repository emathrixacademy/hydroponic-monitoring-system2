"""
HydroVision Pro - Clean Minimalist Version
Streamlined monitoring dashboard with essential information only

Version: 2.1 (Minimalist)
Author: Florence (SET Certification)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# ==================== CONFIGURATION ====================
class Config:
    """System configuration"""
    COLOR_PRIMARY = "#6B21A8"
    COLOR_SECONDARY = "#9333EA"
    COLOR_ACCENT = "#FCD34D"
    COLOR_SUCCESS = "#22C55E"
    COLOR_DANGER = "#EF4444"
    
    PH_TARGET, PH_TOL = 5.8, 0.15
    EC_TARGET, EC_TOL = 1.2, 0.08
    TEMP_MIN, TEMP_MAX = 18.0, 22.0
    
    TEACHABLE_MACHINE_URL = "https://teachablemachine.withgoogle.com/models/GU_vNr8UW/"

# ==================== PAGE SETUP ====================
st.set_page_config(
    page_title="HydroVision Pro",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CLEAN CSS ====================
st.markdown(f"""
<style>
    #MainMenu, footer, header, .stDeployButton {{visibility: hidden;}}
    .main {{padding: 1rem;}}
    
    .hero-card {{
        background: linear-gradient(135deg, {Config.COLOR_PRIMARY} 0%, {Config.COLOR_SECONDARY} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .hero-card h1 {{
        font-size: 2.5rem;
        margin: 0;
        color: {Config.COLOR_ACCENT};
    }}
    
    .metric-box {{
        background: white;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        height: 100%;
    }}
    
    .metric-box.optimal {{border-color: {Config.COLOR_SUCCESS}; background: #F0FDF4;}}
    .metric-box.warning {{border-color: #F59E0B; background: #FFFBEB;}}
    .metric-box.danger {{border-color: {Config.COLOR_DANGER}; background: #FEF2F2;}}
    
    .metric-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {Config.COLOR_PRIMARY};
    }}
    
    .metric-status {{
        font-size: 0.85rem;
        margin-top: 0.5rem;
        color: #4B5563;
    }}
    
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {Config.COLOR_PRIMARY};
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {Config.COLOR_ACCENT};
    }}
</style>
""", unsafe_allow_html=True)

# ==================== DATA SIMULATOR ====================
class DataSim:
    def __init__(self):
        self.step = 0
        
    def get_current(self):
        self.step += 1
        t = datetime.now()
        return {
            'time': t,
            'pH': 5.8 + np.sin(self.step * 0.05) * 0.08 + np.random.normal(0, 0.02),
            'ec': 1.2 + np.sin(self.step * 0.03) * 0.03 + np.random.normal(0, 0.01),
            'temp': 20 + np.random.normal(0, 0.3),
            'air_temp': 25 + np.random.normal(0, 0.5),
            'humidity': 70 + np.random.normal(0, 2),
            'battery': 14.8 - (self.step * 0.0001),
            'water_level': 10 + np.random.normal(0, 0.2)
        }
    
    def get_history(self, hours=6):
        data = []
        for i in range(72):
            t = datetime.now() - timedelta(minutes=i*5)
            data.append({
                'time': t,
                'pH': 5.8 + np.sin(i * 0.1) * 0.1 + np.random.normal(0, 0.03),
                'ec': 1.2 + np.sin(i * 0.08) * 0.05 + np.random.normal(0, 0.015),
                'temp': 20 + np.random.normal(0, 0.3)
            })
        return pd.DataFrame(data[::-1])

# Initialize
if 'sim' not in st.session_state:
    st.session_state.sim = DataSim()

sim = st.session_state.sim
current = sim.get_current()

# ==================== HEADER ====================
st.markdown(f"""
<div class="hero-card">
    <h1>🌱 HydroVision Pro</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Smart IoT Hydroponic Monitoring</p>
    <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
        Last updated: {current['time'].strftime('%I:%M:%S %p')} | Battery: {current['battery']:.2f}V | Water: {current['water_level']:.1f}cm
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== MAIN DASHBOARD ====================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🤖 AI Detection", "📈 Analytics"])

# TAB 1: DASHBOARD
with tab1:
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    # pH Status
    with col1:
        ph_ok = Config.PH_TARGET - Config.PH_TOL <= current['pH'] <= Config.PH_TARGET + Config.PH_TOL
        ph_class = "optimal" if ph_ok else "warning"
        ph_msg = "✓ Optimal" if ph_ok else "⚠ Adjust"
        
        st.markdown(f"""
        <div class="metric-box {ph_class}">
            <div class="metric-label">pH Level</div>
            <div class="metric-value">{current['pH']:.2f}</div>
            <div class="metric-status">{ph_msg}<br>Target: {Config.PH_TARGET} ± {Config.PH_TOL}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # EC Status
    with col2:
        ec_ok = Config.EC_TARGET - Config.EC_TOL <= current['ec'] <= Config.EC_TARGET + Config.EC_TOL
        ec_class = "optimal" if ec_ok else "warning"
        ec_msg = "✓ Optimal" if ec_ok else "⚠ Adjust"
        
        st.markdown(f"""
        <div class="metric-box {ec_class}">
            <div class="metric-label">EC Level</div>
            <div class="metric-value">{current['ec']:.2f}</div>
            <div class="metric-status">{ec_msg}<br>Target: {Config.EC_TARGET} ± {Config.EC_TOL} mS/cm</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Temperature Status
    with col3:
        temp_ok = Config.TEMP_MIN <= current['temp'] <= Config.TEMP_MAX
        temp_class = "optimal" if temp_ok else "warning"
        temp_msg = "✓ Optimal" if temp_ok else "⚠ Check"
        
        st.markdown(f"""
        <div class="metric-box {temp_class}">
            <div class="metric-label">Water Temperature</div>
            <div class="metric-value">{current['temp']:.1f}°C</div>
            <div class="metric-status">{temp_msg}<br>Range: {Config.TEMP_MIN}-{Config.TEMP_MAX}°C</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="section-title">📈 Sensor Trends (Last 6 Hours)</div>', unsafe_allow_html=True)
    
    history = sim.get_history()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_ph = go.Figure()
        fig_ph.add_hline(y=Config.PH_TARGET + Config.PH_TOL, line_dash="dash", line_color="rgba(239,68,68,0.3)")
        fig_ph.add_hline(y=Config.PH_TARGET - Config.PH_TOL, line_dash="dash", line_color="rgba(239,68,68,0.3)")
        fig_ph.add_hline(y=Config.PH_TARGET, line_dash="dot", line_color="rgba(34,197,94,0.5)")
        fig_ph.add_trace(go.Scatter(
            x=history['time'], y=history['pH'],
            mode='lines+markers',
            line=dict(color=Config.COLOR_PRIMARY, width=3),
            marker=dict(size=4),
            name='pH'
        ))
        fig_ph.update_layout(
            title="pH Level",
            height=300,
            margin=dict(l=50, r=20, t=40, b=40),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="pH"
        )
        st.plotly_chart(fig_ph, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig_ec = go.Figure()
        fig_ec.add_hline(y=Config.EC_TARGET + Config.EC_TOL, line_dash="dash", line_color="rgba(239,68,68,0.3)")
        fig_ec.add_hline(y=Config.EC_TARGET - Config.EC_TOL, line_dash="dash", line_color="rgba(239,68,68,0.3)")
        fig_ec.add_hline(y=Config.EC_TARGET, line_dash="dot", line_color="rgba(34,197,94,0.5)")
        fig_ec.add_trace(go.Scatter(
            x=history['time'], y=history['ec'],
            mode='lines+markers',
            line=dict(color=Config.COLOR_SECONDARY, width=3),
            marker=dict(size=4),
            name='EC'
        ))
        fig_ec.update_layout(
            title="EC Level",
            height=300,
            margin=dict(l=50, r=20, t=40, b=40),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis_title="mS/cm"
        )
        st.plotly_chart(fig_ec, use_container_width=True, config={'displayModeBar': False})
    
    # System Info
    st.markdown('<div class="section-title">ℹ️ System Status</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔋 Battery", f"{current['battery']:.2f}V")
    col2.metric("💧 Water Level", f"{current['water_level']:.1f} cm")
    col3.metric("🌡️ Air Temp", f"{current['air_temp']:.1f}°C")
    col4.metric("💨 Humidity", f"{current['humidity']:.1f}%")

# TAB 2: AI DETECTION
with tab2:
    st.markdown('<div class="section-title">🤖 AI Plant Health Scanner</div>', unsafe_allow_html=True)
    st.info("📸 **Instructions:** Point camera at plant → Watch live predictions → Click 'Capture' for detailed analysis")
    
    st.components.v1.html(f"""
    <div style="text-align: center; padding: 20px;">
        <div id="webcam-container"></div>
        
        <button id="capture-btn" style="
            background: linear-gradient(135deg, {Config.COLOR_PRIMARY}, {Config.COLOR_SECONDARY});
            color: white; border: none; padding: 15px 40px;
            font-size: 18px; font-weight: bold; border-radius: 10px;
            cursor: pointer; margin: 20px 0; box-shadow: 0 4px 15px rgba(107,33,168,0.3);">
            📸 Capture & Analyze
        </button>
        
        <div id="live-predictions" style="background: white; border-radius: 12px; 
            padding: 20px; margin: 20px 0; border: 2px solid #E5E7EB;">
            <h3 style="color: {Config.COLOR_PRIMARY}; margin: 0 0 15px 0;">📊 Live Predictions</h3>
            <div id="bars"></div>
        </div>
        
        <div id="result"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>

    <script>
        const URL = "{Config.TEACHABLE_MACHINE_URL}";
        let model, webcam, maxPredictions;
        
        const recs = {{
            'full grown': {{emoji: '🌟', color: '#3B82F6', title: 'Full Grown - Harvest Ready!'}},
            'matured': {{emoji: '✅', color: '#22C55E', title: 'Matured - Healthy Growth'}},
            'sprout': {{emoji: '🌱', color: '#10B981', title: 'Sprout - Early Stage'}},
            'withered': {{emoji: '🚨', color: '#EF4444', title: 'Withered - Needs Attention'}}
        }};

        async function init() {{
            model = await tmImage.load(URL + "model.json", URL + "metadata.json");
            maxPredictions = model.getTotalClasses();
            
            webcam = new tmImage.Webcam(350, 350, true);
            await webcam.setup({{facingMode: "environment"}});
            await webcam.play();
            window.requestAnimationFrame(loop);
            
            document.getElementById("webcam-container").appendChild(webcam.canvas);
            webcam.canvas.style.borderRadius = "12px";
            webcam.canvas.style.boxShadow = "0 4px 20px rgba(0,0,0,0.2)";
            
            const bars = document.getElementById("bars");
            for (let i = 0; i < maxPredictions; i++) {{
                bars.appendChild(document.createElement("div"));
            }}
            
            document.getElementById("capture-btn").onclick = capture;
        }}

        async function loop() {{
            webcam.update();
            const pred = await model.predict(webcam.canvas);
            pred.sort((a, b) => b.probability - a.probability);
            
            const bars = document.getElementById("bars");
            for (let i = 0; i < maxPredictions; i++) {{
                const name = pred[i].className.toLowerCase();
                const prob = (pred[i].probability * 100).toFixed(1);
                const rec = recs[name] || recs['matured'];
                
                bars.childNodes[i].innerHTML = `
                    <div style="margin: 12px 0; text-align: left;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="font-weight: 600; color: #1F2937;">${{i === 0 ? '🎯 ' : ''}}${{pred[i].className}}</span>
                            <span style="font-weight: 700; color: ${{rec.color}};">${{prob}}%</span>
                        </div>
                        <div style="background: #E5E7EB; border-radius: 8px; height: 25px; overflow: hidden;">
                            <div style="background: ${{i === 0 ? rec.color : '#D1D5DB'}}; width: ${{prob}}%; 
                                height: 100%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                `;
            }}
            
            window.requestAnimationFrame(loop);
        }}

        async function capture() {{
            const btn = document.getElementById("capture-btn");
            btn.innerHTML = "🔄 Analyzing...";
            btn.disabled = true;
            
            const pred = await model.predict(webcam.canvas);
            pred.sort((a, b) => b.probability - a.probability);
            
            const top = pred[0];
            const name = top.className.toLowerCase();
            const conf = (top.probability * 100).toFixed(1);
            const rec = recs[name] || recs['matured'];
            
            document.getElementById("result").innerHTML = `
                <div style="background: white; border: 3px solid ${{rec.color}}; 
                    border-radius: 15px; padding: 30px; margin: 20px 0; text-align: center;">
                    <div style="font-size: 4rem;">${{rec.emoji}}</div>
                    <h2 style="color: ${{rec.color}}; margin: 15px 0;">${{rec.title}}</h2>
                    <div style="font-size: 2rem; font-weight: 700; color: {Config.COLOR_PRIMARY};">${{conf}}%</div>
                    <p style="color: #6B7280; margin-top: 10px;">AI Confidence Score</p>
                </div>
            `;
            
            setTimeout(() => {{
                btn.innerHTML = "📸 Capture Again";
                btn.disabled = false;
            }}, 1000);
        }}

        init();
    </script>
    """, height=1400)

# TAB 3: ANALYTICS
with tab3:
    st.markdown('<div class="section-title">📊 Statistical Analysis</div>', unsafe_allow_html=True)
    
    time_range = st.selectbox("📅 Time Period", ["Last 6 Hours", "Last 12 Hours", "Last 24 Hours"])
    
    history = sim.get_history()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("**pH** Average", f"{history['pH'].mean():.2f} pH")
        st.metric("**pH** Std Dev", f"±{history['pH'].std():.3f}")
    
    with col2:
        st.metric("**EC** Average", f"{history['ec'].mean():.2f} mS/cm")
        st.metric("**EC** Std Dev", f"±{history['ec'].std():.3f}")
    
    with col3:
        st.metric("**Temperature** Average", f"{history['temp'].mean():.1f}°C")
        st.metric("**Temperature** Range", f"{history['temp'].max() - history['temp'].min():.1f}°C")
    
    # Multi-metric chart
    st.markdown('<div class="section-title">📈 Multi-Parameter Trends</div>', unsafe_allow_html=True)
    
    fig = make_subplots(rows=1, cols=3, subplot_titles=['pH', 'EC (mS/cm)', 'Temperature (°C)'])
    
    fig.add_trace(go.Scatter(x=history['time'], y=history['pH'], 
        line=dict(color=Config.COLOR_PRIMARY, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=history['time'], y=history['ec'],
        line=dict(color=Config.COLOR_SECONDARY, width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=history['time'], y=history['temp'],
        line=dict(color='#06B6D4', width=2)), row=1, col=3)
    
    fig.update_layout(height=350, showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Raw data
    with st.expander("📋 View Raw Data"):
        st.dataframe(history.style.format({
            'pH': '{:.2f}', 'ec': '{:.2f}', 'temp': '{:.1f}'
        }), use_container_width=True, height=300)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    <strong>HydroVision Pro</strong> by SET Certification | PUP Sta. Rosa Campus<br>
    IoT Hydroponic Monitoring System | Version 2.1
</div>
""", unsafe_allow_html=True)

# Auto-refresh
time.sleep(3)
st.rerun()
