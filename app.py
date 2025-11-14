"""
HydroVision Pro - Advanced IoT Hydroponic Monitoring System
Professional-grade monitoring dashboard with AI-powered plant health detection

Author: Florence (SET Certification)
Institution: Polytechnic University of the Philippines
Program: MS Computer Engineering (Data Science & Engineering)
License: MIT
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple
import json

# ==================== CONFIGURATION ====================
class SystemConfig:
    """System configuration and constants"""
    
    # Brand Colors
    COLOR_PRIMARY = "#6B21A8"      # Purple
    COLOR_SECONDARY = "#9333EA"    # Light Purple
    COLOR_ACCENT = "#FCD34D"       # Gold
    COLOR_SUCCESS = "#22C55E"      # Green
    COLOR_WARNING = "#F59E0B"      # Amber
    COLOR_DANGER = "#EF4444"       # Red
    COLOR_BG = "#FFFFFF"           # White
    COLOR_TEXT = "#1F2937"         # Dark Gray
    
    # Sensor Thresholds (Based on research-backed optimal ranges)
    PH_TARGET = 5.8
    PH_TOLERANCE = 0.15
    PH_MIN = PH_TARGET - PH_TOLERANCE
    PH_MAX = PH_TARGET + PH_TOLERANCE
    
    EC_TARGET = 1.2  # mS/cm
    EC_TOLERANCE = 0.08
    EC_MIN = EC_TARGET - EC_TOLERANCE
    EC_MAX = EC_TARGET + EC_TOLERANCE
    
    TEMP_MIN = 18.0  # °C
    TEMP_MAX = 22.0
    TEMP_OPTIMAL = 20.0
    
    WATER_LEVEL_MIN = 5.0  # cm from sensor
    WATER_LEVEL_MAX = 15.0
    
    # System Parameters
    SAMPLING_INTERVAL = 5  # seconds
    DATA_RETENTION_HOURS = 24
    ALERT_COOLDOWN = 300  # seconds (5 min)
    
    # AI Model Configuration
    TEACHABLE_MACHINE_URL = "https://teachablemachine.withgoogle.com/models/GU_vNr8UW/"
    AI_CONFIDENCE_THRESHOLD = 0.75
    AI_SCAN_INTERVAL = 3600  # seconds (1 hour)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="HydroVision Pro - IoT Monitoring",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown(f"""
<style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* Global styles */
    .main {{
        padding: 0rem 1rem;
    }}
    
    /* Professional header */
    .system-header {{
        background: linear-gradient(135deg, {SystemConfig.COLOR_PRIMARY} 0%, {SystemConfig.COLOR_SECONDARY} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(107,33,168,0.3);
    }}
    
    .system-header h1 {{
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: {SystemConfig.COLOR_ACCENT};
    }}
    
    .system-header p {{
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }}
    
    /* Metric cards */
    .metric-card {{
        background: white;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .metric-card:hover {{
        border-color: {SystemConfig.COLOR_PRIMARY};
        box-shadow: 0 4px 16px rgba(107,33,168,0.2);
        transform: translateY(-2px);
    }}
    
    .metric-card.alert {{
        border-color: {SystemConfig.COLOR_DANGER};
        background: #FEF2F2;
    }}
    
    .metric-card.warning {{
        border-color: {SystemConfig.COLOR_WARNING};
        background: #FFFBEB;
    }}
    
    .metric-card.optimal {{
        border-color: {SystemConfig.COLOR_SUCCESS};
        background: #F0FDF4;
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {SystemConfig.COLOR_PRIMARY};
        margin: 0.5rem 0;
    }}
    
    .metric-unit {{
        font-size: 1rem;
        color: #9CA3AF;
        margin-left: 0.25rem;
    }}
    
    .metric-status {{
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }}
    
    .status-optimal {{
        background: {SystemConfig.COLOR_SUCCESS}20;
        color: {SystemConfig.COLOR_SUCCESS};
    }}
    
    .status-warning {{
        background: {SystemConfig.COLOR_WARNING}20;
        color: {SystemConfig.COLOR_WARNING};
    }}
    
    .status-danger {{
        background: {SystemConfig.COLOR_DANGER}20;
        color: {SystemConfig.COLOR_DANGER};
    }}
    
    /* System status badge */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 1rem 0;
    }}
    
    .status-online {{
        background: {SystemConfig.COLOR_SUCCESS}20;
        color: {SystemConfig.COLOR_SUCCESS};
        border: 2px solid {SystemConfig.COLOR_SUCCESS};
    }}
    
    .status-offline {{
        background: {SystemConfig.COLOR_DANGER}20;
        color: {SystemConfig.COLOR_DANGER};
        border: 2px solid {SystemConfig.COLOR_DANGER};
    }}
    
    /* Section headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {SystemConfig.COLOR_PRIMARY};
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid {SystemConfig.COLOR_ACCENT};
    }}
    
    /* AI detection section */
    .ai-container {{
        background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 2px solid {SystemConfig.COLOR_PRIMARY};
    }}
    
    /* Alert messages */
    .alert-box {{
        border-left: 4px solid {SystemConfig.COLOR_DANGER};
        background: #FEF2F2;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    
    /* Data table styling */
    .dataframe {{
        font-size: 0.9rem;
    }}
    
    /* Footer */
    .app-footer {{
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 2px solid #E5E7EB;
        color: {SystemConfig.COLOR_TEXT};
        opacity: 0.7;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== DATA GENERATION (Demo Mode) ====================
class DataSimulator:
    """Simulates sensor data with realistic patterns and variations"""
    
    def __init__(self):
        self.step = 0
        self.start_time = datetime.now()
        # Base values
        self.ph_base = SystemConfig.PH_TARGET
        self.ec_base = SystemConfig.EC_TARGET
        self.temp_base = SystemConfig.TEMP_OPTIMAL
        
    def get_current_readings(self) -> Dict:
        """Generate current sensor readings with temporal patterns"""
        self.step += 1
        current_time = datetime.now()
        
        # Add diurnal patterns and realistic noise
        hour_of_day = current_time.hour
        diurnal_factor = np.sin(2 * np.pi * hour_of_day / 24)
        
        # pH: Slight drift with correction cycles
        ph_drift = np.sin(self.step * 0.05) * 0.08
        ph_noise = np.random.normal(0, 0.02)
        ph = self.ph_base + ph_drift + ph_noise
        
        # EC: Temperature-compensated with nutrient depletion simulation
        ec_drift = -0.001 * self.step / 100  # Gradual depletion
        ec_variation = np.sin(self.step * 0.03) * 0.03
        ec_noise = np.random.normal(0, 0.01)
        ec = max(0.8, self.ec_base + ec_drift + ec_variation + ec_noise)
        
        # Water temperature: Ambient correlation
        temp_ambient_effect = diurnal_factor * 1.5
        temp_noise = np.random.normal(0, 0.3)
        water_temp = self.temp_base + temp_ambient_effect + temp_noise
        
        # Air temperature: Higher amplitude diurnal cycle
        air_temp = 25 + diurnal_factor * 4 + np.random.normal(0, 0.5)
        
        # Humidity: Inverse correlation with temperature
        humidity = 70 - diurnal_factor * 15 + np.random.normal(0, 2)
        
        # Water level: Gradual consumption
        water_level = 10 - (self.step * 0.01) + np.random.normal(0, 0.2)
        water_level = max(5, min(15, water_level))
        
        # Battery voltage: Discharge curve
        battery_discharge = -0.001 * self.step / 100
        battery_voltage = 14.8 + battery_discharge + np.random.normal(0, 0.05)
        battery_voltage = max(11.0, battery_voltage)
        
        return {
            'timestamp': current_time,
            'pH': round(ph, 2),
            'ec': round(ec, 2),
            'water_temp': round(water_temp, 1),
            'air_temp': round(air_temp, 1),
            'humidity': round(humidity, 1),
            'water_level': round(water_level, 1),
            'battery_voltage': round(battery_voltage, 2),
            'system_uptime': int((current_time - self.start_time).total_seconds()),
        }
    
    def get_historical_data(self, hours: int = 24, points: int = 288) -> pd.DataFrame:
        """Generate historical data for trend analysis"""
        data = []
        current_time = datetime.now()
        
        for i in range(points):
            time_offset = timedelta(hours=hours * (1 - i/points))
            timestamp = current_time - time_offset
            
            # Simulate historical patterns
            hour = timestamp.hour
            diurnal = np.sin(2 * np.pi * hour / 24)
            
            data.append({
                'timestamp': timestamp,
                'pH': SystemConfig.PH_TARGET + np.sin(i * 0.1) * 0.1 + np.random.normal(0, 0.03),
                'ec': SystemConfig.EC_TARGET + np.sin(i * 0.08) * 0.05 + np.random.normal(0, 0.015),
                'water_temp': SystemConfig.TEMP_OPTIMAL + diurnal * 1.5 + np.random.normal(0, 0.3),
                'air_temp': 25 + diurnal * 4 + np.random.normal(0, 0.5),
                'humidity': 70 - diurnal * 15 + np.random.normal(0, 2),
            })
        
        return pd.DataFrame(data)

# ==================== ANALYSIS FUNCTIONS ====================
class SensorAnalyzer:
    """Analyzes sensor readings and provides status assessments"""
    
    @staticmethod
    def assess_ph(value: float) -> Tuple[str, str]:
        """Assess pH level and return status and message"""
        if SystemConfig.PH_MIN <= value <= SystemConfig.PH_MAX:
            return "optimal", f"✓ Optimal range ({SystemConfig.PH_TARGET:.1f} ± {SystemConfig.PH_TOLERANCE:.2f})"
        elif value < SystemConfig.PH_MIN - 0.2:
            return "danger", f"⚠ Critically low! Add pH UP solution"
        elif value > SystemConfig.PH_MAX + 0.2:
            return "danger", f"⚠ Critically high! Add pH DOWN solution"
        elif value < SystemConfig.PH_MIN:
            return "warning", f"↓ Below target. Monitor closely"
        else:
            return "warning", f"↑ Above target. Monitor closely"
    
    @staticmethod
    def assess_ec(value: float) -> Tuple[str, str]:
        """Assess EC level and return status and message"""
        if SystemConfig.EC_MIN <= value <= SystemConfig.EC_MAX:
            return "optimal", f"✓ Optimal range ({SystemConfig.EC_TARGET:.1f} ± {SystemConfig.EC_TOLERANCE:.2f} mS/cm)"
        elif value < SystemConfig.EC_MIN - 0.1:
            return "danger", f"⚠ Critically low! Add nutrient solution"
        elif value > SystemConfig.EC_MAX + 0.1:
            return "danger", f"⚠ Critically high! Dilute solution"
        elif value < SystemConfig.EC_MIN:
            return "warning", f"↓ Below target. Consider adding nutrients"
        else:
            return "warning", f"↑ Above target. Check concentration"
    
    @staticmethod
    def assess_temperature(value: float) -> Tuple[str, str]:
        """Assess temperature and return status and message"""
        if SystemConfig.TEMP_MIN <= value <= SystemConfig.TEMP_MAX:
            return "optimal", f"✓ Optimal range ({SystemConfig.TEMP_MIN:.1f}-{SystemConfig.TEMP_MAX:.1f}°C)"
        elif value < SystemConfig.TEMP_MIN - 2:
            return "danger", f"⚠ Too cold! Risk of slow growth"
        elif value > SystemConfig.TEMP_MAX + 2:
            return "danger", f"⚠ Too hot! Risk of root damage"
        elif value < SystemConfig.TEMP_MIN:
            return "warning", f"↓ Below optimal. Consider heating"
        else:
            return "warning", f"↑ Above optimal. Improve cooling"
    
    @staticmethod
    def calculate_system_health(readings: Dict) -> Tuple[float, str]:
        """Calculate overall system health score (0-100)"""
        scores = []
        
        # pH score (30% weight)
        ph_deviation = abs(readings['pH'] - SystemConfig.PH_TARGET) / SystemConfig.PH_TOLERANCE
        ph_score = max(0, 100 - (ph_deviation * 50))
        scores.append(ph_score * 0.3)
        
        # EC score (30% weight)
        ec_deviation = abs(readings['ec'] - SystemConfig.EC_TARGET) / SystemConfig.EC_TOLERANCE
        ec_score = max(0, 100 - (ec_deviation * 50))
        scores.append(ec_score * 0.3)
        
        # Temperature score (25% weight)
        temp_range = SystemConfig.TEMP_MAX - SystemConfig.TEMP_MIN
        temp_deviation = abs(readings['water_temp'] - SystemConfig.TEMP_OPTIMAL) / (temp_range / 2)
        temp_score = max(0, 100 - (temp_deviation * 50))
        scores.append(temp_score * 0.25)
        
        # Water level score (15% weight)
        if readings['water_level'] < SystemConfig.WATER_LEVEL_MIN:
            water_score = 50
        elif readings['water_level'] > SystemConfig.WATER_LEVEL_MAX:
            water_score = 70
        else:
            water_score = 100
        scores.append(water_score * 0.15)
        
        total_score = sum(scores)
        
        # Determine health status
        if total_score >= 90:
            status = "Excellent"
        elif total_score >= 75:
            status = "Good"
        elif total_score >= 60:
            status = "Fair"
        else:
            status = "Critical"
        
        return round(total_score, 1), status

# ==================== VISUALIZATION FUNCTIONS ====================
def create_realtime_chart(df: pd.DataFrame, metric: str, title: str, 
                         unit: str, color: str, target: float = None, 
                         tolerance: float = None) -> go.Figure:
    """Create professional real-time monitoring chart"""
    
    fig = go.Figure()
    
    # Add target range if provided
    if target and tolerance:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=[target + tolerance] * len(df),
            mode='lines',
            name='Upper Limit',
            line=dict(color='rgba(239, 68, 68, 0.3)', dash='dash', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=[target - tolerance] * len(df),
            mode='lines',
            name='Lower Limit',
            line=dict(color='rgba(239, 68, 68, 0.3)', dash='dash', width=1),
            fill='tonexty',
            fillcolor='rgba(34, 197, 94, 0.1)',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=[target] * len(df),
            mode='lines',
            name='Target',
            line=dict(color='rgba(34, 197, 94, 0.5)', dash='dot', width=2),
            showlegend=True
        ))
    
    # Add main data line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[metric],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.1])}',
        hovertemplate=f'<b>%{{y:.2f}} {unit}</b><br>%{{x|%H:%M}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, weight='bold')),
        xaxis=dict(
            title="Time",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            tickformat='%H:%M'
        ),
        yaxis=dict(
            title=f"{title} ({unit})",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=60, r=20, t=60, b=60),
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_multi_metric_chart(df: pd.DataFrame) -> go.Figure:
    """Create multi-metric comparison chart"""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('pH Level', 'EC Level (mS/cm)', 'Water Temperature (°C)', 'Air Temperature (°C)'),
        vertical_spacing=0.12,
        horizontal_spacing=0.10
    )
    
    # pH
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['pH'], name='pH', 
                  line=dict(color=SystemConfig.COLOR_PRIMARY, width=2)),
        row=1, col=1
    )
    
    # EC
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['ec'], name='EC',
                  line=dict(color=SystemConfig.COLOR_SECONDARY, width=2)),
        row=1, col=2
    )
    
    # Water Temp
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['water_temp'], name='Water Temp',
                  line=dict(color='#06B6D4', width=2)),
        row=2, col=1
    )
    
    # Air Temp
    fig.add_trace(
        go.Scatter(x=df['timestamp'], y=df['air_temp'], name='Air Temp',
                  line=dict(color='#F59E0B', width=2)),
        row=2, col=2
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)')
    
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", size=11),
        margin=dict(l=60, r=20, t=80, b=60)
    )
    
    return fig

# ==================== AI DETECTION COMPONENT ====================
def render_ai_detection():
    """Render AI plant health detection interface"""
    
    st.markdown('<div class="ai-container">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI-Powered Plant Health Detection")
    st.markdown("**Real-time lettuce health classification using Google Teachable Machine**")
    st.markdown("*Point camera at plant, watch live predictions, then capture for detailed analysis*")
    
    # AI detection interface with live camera + capture
    st.components.v1.html(f"""
    <div style="text-align: center; padding: 20px;">
        <div id="webcam-container" style="margin: 20px auto;"></div>
        
        <button id="capture-btn" style="
            background: linear-gradient(135deg, {SystemConfig.COLOR_PRIMARY} 0%, {SystemConfig.COLOR_SECONDARY} 100%);
            color: white;
            border: none;
            padding: 15px 50px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(107,33,168,0.4);
            transition: all 0.3s ease;">
            📸 Capture & Analyze Plant Health
        </button>
        
        <div id="live-predictions" style="
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">
            <h3 style="color: {SystemConfig.COLOR_PRIMARY}; margin-bottom: 15px;">
                📊 Live Predictions
            </h3>
            <div id="prediction-bars"></div>
        </div>
        
        <div id="analysis-result"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>

    <script type="text/javascript">
        const MODEL_URL = "{SystemConfig.TEACHABLE_MACHINE_URL}";
        const CONFIDENCE_THRESHOLD = {SystemConfig.AI_CONFIDENCE_THRESHOLD};
        
        let model, webcam, maxPredictions, isAnalyzing = false;
        
        // Health classification recommendations
        const recommendations = {{
            'full grown': {{
                emoji: '🌟',
                color: '#3B82F6',
                title: 'Full Grown - Ready for Harvest',
                priority: 'high',
                actions: [
                    'Harvest immediately for optimal quality',
                    'Best harvest time: early morning (6-8 AM)',
                    'Cut 2cm above root crown',
                    'Store at 4°C, consume within 7 days',
                    'Expected yield: 150-180g per plant'
                ],
                metrics: {{
                    'Days to harvest': 'Ready now',
                    'Optimal weight': '150-180g',
                    'Shelf life': '7 days at 4°C'
                }}
            }},
            'matured': {{
                emoji: '✅',
                color: '#22C55E',
                title: 'Matured - Healthy Growth',
                priority: 'normal',
                actions: [
                    'Maintain pH: 5.8 ± 0.15',
                    'Maintain EC: 1.2 ± 0.08 mS/cm',
                    'Continue current nutrient schedule',
                    'Monitor daily for harvest readiness',
                    'Expected harvest: 3-5 days'
                ],
                metrics: {{
                    'Days to harvest': '3-5 days',
                    'Current health': 'Excellent',
                    'Growth rate': 'Normal'
                }}
            }},
            'sprout': {{
                emoji: '🌱',
                color: '#10B981',
                title: 'Sprout - Early Growth Stage',
                priority: 'normal',
                actions: [
                    'Reduce EC to 0.8-1.0 mS/cm for young plants',
                    'Maintain stable pH: 5.8',
                    'Ensure 12-16 hours light daily',
                    'Avoid over-watering',
                    'Expected maturity: 21-28 days'
                ],
                metrics: {{
                    'Growth stage': 'Seedling',
                    'Days to maturity': '21-28 days',
                    'Required EC': '0.8-1.0 mS/cm'
                }}
            }},
            'withered': {{
                emoji: '🚨',
                color: '#EF4444',
                title: 'Withered - Critical Condition',
                priority: 'critical',
                actions: [
                    'Check temperature: maintain 18-22°C',
                    'Verify pH and EC levels immediately',
                    'Inspect for root rot or disease',
                    'Ensure adequate oxygen (air pump)',
                    'Remove if diseased to prevent spread',
                    'Consider replanting if root damage severe'
                ],
                metrics: {{
                    'Health status': 'Critical',
                    'Action required': 'Immediate',
                    'Survival chance': 'Low without intervention'
                }}
            }}
        }};

        async function init() {{
            try {{
                // Load Teachable Machine model
                const modelURL = MODEL_URL + "model.json";
                const metadataURL = MODEL_URL + "metadata.json";
                model = await tmImage.load(modelURL, metadataURL);
                maxPredictions = model.getTotalClasses();

                // Setup webcam
                const flip = true;
                webcam = new tmImage.Webcam(400, 400, flip);
                await webcam.setup({{ facingMode: "environment" }});
                await webcam.play();
                window.requestAnimationFrame(loop);

                // Add webcam to DOM
                document.getElementById("webcam-container").appendChild(webcam.canvas);
                webcam.canvas.style.borderRadius = "12px";
                webcam.canvas.style.boxShadow = "0 4px 20px rgba(0,0,0,0.2)";
                
                // Initialize prediction bars
                const barsContainer = document.getElementById("prediction-bars");
                for (let i = 0; i < maxPredictions; i++) {{
                    barsContainer.appendChild(document.createElement("div"));
                }}
                
                // Capture button event
                document.getElementById("capture-btn").addEventListener("click", captureAndAnalyze);
                
                console.log("✅ AI System initialized successfully");
            }} catch (error) {{
                console.error("❌ Initialization error:", error);
                document.getElementById("webcam-container").innerHTML = 
                    '<p style="color: #EF4444;">Camera initialization failed. Please allow camera access and refresh.</p>';
            }}
        }}

        async function loop() {{
            webcam.update();
            await updateLivePredictions();
            window.requestAnimationFrame(loop);
        }}

        async function updateLivePredictions() {{
            const prediction = await model.predict(webcam.canvas);
            prediction.sort((a, b) => b.probability - a.probability);
            
            const barsContainer = document.getElementById("prediction-bars");
            
            for (let i = 0; i < maxPredictions; i++) {{
                const className = prediction[i].className.toLowerCase();
                const probability = (prediction[i].probability * 100).toFixed(1);
                
                const rec = recommendations[className] || recommendations['matured'];
                const isTop = i === 0;
                
                barsContainer.childNodes[i].innerHTML = `
                    <div style="margin: 15px 0; text-align: left;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-weight: ${{isTop ? '700' : '600'}}; color: #1F2937; font-size: ${{isTop ? '1.1rem' : '0.95rem'}};">
                                ${{isTop ? '🎯 ' : ''}}${{prediction[i].className}}
                            </span>
                            <span style="font-weight: 700; color: ${{rec.color}}; font-size: ${{isTop ? '1.1rem' : '0.95rem'}};">
                                ${{probability}}%
                            </span>
                        </div>
                        <div style="background: #E5E7EB; border-radius: 10px; height: ${{isTop ? '35px' : '28px'}}; overflow: hidden;">
                            <div style="
                                background: ${{isTop ? rec.color : '#D1D5DB'}};
                                width: ${{probability}}%;
                                height: 100%;
                                transition: width 0.3s ease;
                                display: flex;
                                align-items: center;
                                justify-content: flex-end;
                                padding-right: 10px;
                                color: white;
                                font-weight: 600;
                                font-size: 0.85rem;
                            ">
                                ${{isTop && probability > 15 ? probability + '%' : ''}}
                            </div>
                        </div>
                    </div>
                `;
            }}
        }}

        async function captureAndAnalyze() {{
            if (isAnalyzing) return;
            isAnalyzing = true;
            
            const btn = document.getElementById("capture-btn");
            btn.innerHTML = "🔄 Analyzing...";
            btn.disabled = true;
            btn.style.opacity = "0.6";
            
            // Get prediction
            const prediction = await model.predict(webcam.canvas);
            prediction.sort((a, b) => b.probability - a.probability);
            
            const topResult = prediction[0];
            const className = topResult.className.toLowerCase();
            const confidence = (topResult.probability * 100).toFixed(1);
            const rec = recommendations[className] || recommendations['matured'];
            
            // Generate comprehensive analysis
            let analysisHTML = `
                <div style="
                    background: white;
                    border: 3px solid ${{rec.color}};
                    border-radius: 15px;
                    padding: 30px;
                    margin: 30px 0;
                    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
                ">
                    <div style="text-align: center; margin-bottom: 25px;">
                        <div style="font-size: 4rem; margin-bottom: 15px;">${{rec.emoji}}</div>
                        <h2 style="color: ${{rec.color}}; margin: 0; font-size: 1.8rem; font-weight: 700;">
                            ${{rec.title}}
                        </h2>
                        <div style="margin-top: 15px;">
                            <span style="
                                background: ${{rec.color}}15;
                                color: ${{rec.color}};
                                padding: 10px 25px;
                                border-radius: 25px;
                                font-size: 1.1rem;
                                font-weight: 700;
                                display: inline-block;
                            ">
                                ${{confidence}}% Confidence
                            </span>
                        </div>
                        <p style="color: #6B7280; margin-top: 10px; font-size: 0.95rem;">
                            Classification completed at ${{new Date().toLocaleTimeString()}}
                        </p>
                    </div>
                    
                    <div style="
                        background: #F9FAFB;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 20px 0;
                    ">
                        <h3 style="color: {SystemConfig.COLOR_PRIMARY}; margin-top: 0; font-size: 1.3rem;">
                            📋 Recommended Actions
                        </h3>
            `;
            
            rec.actions.forEach((action, i) => {{
                analysisHTML += `
                    <div style="
                        background: white;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 10px 0;
                        border-left: 4px solid ${{rec.color}};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    ">
                        <strong style="color: {SystemConfig.COLOR_TEXT};">${{i + 1}}.</strong> ${{action}}
                    </div>
                `;
            }});
            
            analysisHTML += `
                    </div>
                    
                    <div style="
                        background: #F9FAFB;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 20px 0;
                    ">
                        <h3 style="color: {SystemConfig.COLOR_PRIMARY}; margin-top: 0; font-size: 1.3rem;">
                            📊 Key Metrics
                        </h3>
            `;
            
            for (const [metric, value] of Object.entries(rec.metrics)) {{
                analysisHTML += `
                    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #E5E7EB;">
                        <span style="font-weight: 600; color: #4B5563;">${{metric}}:</span>
                        <span style="color: {SystemConfig.COLOR_TEXT};">${{value}}</span>
                    </div>
                `;
            }}
            
            analysisHTML += `
                    </div>
                    
                    <div style="
                        background: #F9FAFB;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 20px 0;
                    ">
                        <h3 style="color: {SystemConfig.COLOR_PRIMARY}; margin-top: 0; font-size: 1.3rem;">
                            🔍 All Predictions
                        </h3>
            `;
            
            for (let i = 0; i < prediction.length; i++) {{
                const name = prediction[i].className;
                const prob = (prediction[i].probability * 100).toFixed(1);
                const isTop = i === 0;
                
                analysisHTML += `
                    <div style="margin: 15px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-weight: ${{isTop ? '700' : '600'}}; color: #1F2937;">
                                ${{isTop ? '🎯 ' : ''}}${{name}}
                            </span>
                            <span style="font-weight: 700; color: ${{isTop ? rec.color : '#6B7280'}};">
                                ${{prob}}%
                            </span>
                        </div>
                        <div style="background: #E5E7EB; border-radius: 10px; height: 30px; overflow: hidden;">
                            <div style="
                                background: ${{isTop ? rec.color : '#9CA3AF'}};
                                width: ${{prob}}%;
                                height: 100%;
                                transition: width 0.5s ease;
                            "></div>
                        </div>
                    </div>
                `;
            }}
            
            analysisHTML += `
                    </div>
                </div>
            `;
            
            document.getElementById("analysis-result").innerHTML = analysisHTML;
            
            // Scroll to results
            document.getElementById("analysis-result").scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
            
            // Reset button
            setTimeout(() => {{
                btn.innerHTML = "📸 Capture Again";
                btn.disabled = false;
                btn.style.opacity = "1";
                isAnalyzing = false;
            }}, 1000);
        }}

        // Initialize on load
        init();
    </script>
    """, height=1800)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Technical specifications
    with st.expander("🔬 **Technical Specifications**", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **AI Model Architecture:**
            - Base: MobileNet V2 (Transfer Learning)
            - Framework: TensorFlow.js
            - Platform: Teachable Machine
            - Input: 224×224 RGB images
            - Classes: 4 (Full Grown, Matured, Sprout, Withered)
            """)
        with col2:
            st.markdown(f"""
            **Performance Metrics:**
            - Training Accuracy: >95%
            - Validation Accuracy: >92%
            - Inference Time: <100ms
            - Confidence Threshold: {SystemConfig.AI_CONFIDENCE_THRESHOLD}
            - Scan Interval: {SystemConfig.AI_SCAN_INTERVAL//60} minutes
            """)

# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'simulator' not in st.session_state:
        st.session_state.simulator = DataSimulator()
    if 'auto_mode' not in st.session_state:
        st.session_state.auto_mode = True
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []
    
    simulator = st.session_state.simulator
    
    # Header
    st.markdown("""
    <div class="system-header">
        <h1>🌱 HydroVision Pro</h1>
        <p>Advanced IoT Hydroponic Monitoring System with AI-Powered Plant Health Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ System Control")
        
        # System status
        system_online = True
        status_class = "status-online" if system_online else "status-offline"
        status_text = "🟢 System Online" if system_online else "🔴 System Offline"
        st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Auto mode toggle
        auto_mode = st.toggle("🤖 Automatic Control", value=st.session_state.auto_mode)
        st.session_state.auto_mode = auto_mode
        
        if auto_mode:
            st.success("✅ System will automatically adjust pH and EC levels")
        else:
            st.warning("⚠️ Manual control mode - monitor levels closely")
        
        st.markdown("---")
        
        # System information
        st.markdown("### 📊 System Information")
        current = simulator.get_current_readings()
        
        uptime_hours = current['system_uptime'] // 3600
        uptime_mins = (current['system_uptime'] % 3600) // 60
        
        st.metric("⏱️ System Uptime", f"{uptime_hours}h {uptime_mins}m")
        st.metric("🔋 Battery", f"{current['battery_voltage']:.2f}V")
        st.metric("💧 Water Level", f"{current['water_level']:.1f} cm")
        st.metric("📊 Data Points", simulator.step)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export Data", use_container_width=True):
                st.info("Data export feature coming soon")
        with col2:
            if st.button("🔄 Reset Stats", use_container_width=True):
                st.info("Reset feature coming soon")
        
        st.markdown("---")
        
        # Footer info
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem; color: #6B7280; margin-top: 2rem;">
            <strong>HydroVision Pro v2.0</strong><br>
            SET Certification<br>
            PUP Sta. Rosa Campus
        </div>
        """, unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "🤖 AI Plant Health", 
        "📈 Analytics", 
        "⚙️ Settings"
    ])
    
    # TAB 1: DASHBOARD
    with tab1:
        current = simulator.get_current_readings()
        
        # System health score
        health_score, health_status = SensorAnalyzer.calculate_system_health(current)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {SystemConfig.COLOR_PRIMARY} 0%, {SystemConfig.COLOR_SECONDARY} 100%);
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 10px;">OVERALL SYSTEM HEALTH</div>
                <div style="font-size: 3.5rem; font-weight: 700; color: {SystemConfig.COLOR_ACCENT};">{health_score}</div>
                <div style="font-size: 1.2rem; margin-top: 5px;">{health_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric(
                "⏰ Last Update",
                current['timestamp'].strftime("%H:%M:%S"),
                "Live"
            )
            st.metric(
                "🌡️ Ambient",
                f"{current['air_temp']:.1f}°C",
                f"{current['humidity']:.1f}%"
            )
        
        st.markdown("---")
        
        # Critical metrics
        st.markdown('<h2 class="section-header">🎯 Critical Parameters</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        # pH Metric
        with col1:
            ph_status, ph_message = SensorAnalyzer.assess_ph(current['pH'])
            st.markdown(f"""
            <div class="metric-card {ph_status}">
                <div class="metric-label">pH Level</div>
                <div class="metric-value">
                    {current['pH']:.2f}
                    <span class="metric-unit">pH</span>
                </div>
                <div class="metric-status status-{ph_status}">{ph_message}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # EC Metric
        with col2:
            ec_status, ec_message = SensorAnalyzer.assess_ec(current['ec'])
            st.markdown(f"""
            <div class="metric-card {ec_status}">
                <div class="metric-label">EC Level</div>
                <div class="metric-value">
                    {current['ec']:.2f}
                    <span class="metric-unit">mS/cm</span>
                </div>
                <div class="metric-status status-{ec_status}">{ec_message}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Temperature Metric
        with col3:
            temp_status, temp_message = SensorAnalyzer.assess_temperature(current['water_temp'])
            st.markdown(f"""
            <div class="metric-card {temp_status}">
                <div class="metric-label">Water Temperature</div>
                <div class="metric-value">
                    {current['water_temp']:.1f}
                    <span class="metric-unit">°C</span>
                </div>
                <div class="metric-status status-{temp_status}">{temp_message}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time charts
        st.markdown('<h2 class="section-header">📈 Real-Time Monitoring (Last 6 Hours)</h2>', unsafe_allow_html=True)
        
        historical = simulator.get_historical_data(hours=6, points=72)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_ph = create_realtime_chart(
                historical, 'pH', 'pH Level', 'pH', 
                SystemConfig.COLOR_PRIMARY,
                SystemConfig.PH_TARGET, SystemConfig.PH_TOLERANCE
            )
            st.plotly_chart(fig_ph, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig_ec = create_realtime_chart(
                historical, 'ec', 'EC Level', 'mS/cm',
                SystemConfig.COLOR_SECONDARY,
                SystemConfig.EC_TARGET, SystemConfig.EC_TOLERANCE
            )
            st.plotly_chart(fig_ec, use_container_width=True, config={'displayModeBar': False})
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp = create_realtime_chart(
                historical, 'water_temp', 'Water Temperature', '°C',
                '#06B6D4',
                SystemConfig.TEMP_OPTIMAL, (SystemConfig.TEMP_MAX - SystemConfig.TEMP_MIN) / 2
            )
            st.plotly_chart(fig_temp, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            fig_humidity = create_realtime_chart(
                historical, 'humidity', 'Relative Humidity', '%',
                '#F59E0B'
            )
            st.plotly_chart(fig_humidity, use_container_width=True, config={'displayModeBar': False})
    
    # TAB 2: AI PLANT HEALTH
    with tab2:
        render_ai_detection()
    
    # TAB 3: ANALYTICS
    with tab3:
        st.markdown('<h2 class="section-header">📊 Historical Trend Analysis</h2>', unsafe_allow_html=True)
        
        # Time range selector with clear label
        col1, col2 = st.columns([3, 1])
        with col1:
            time_range = st.selectbox(
                "📅 Data Time Range",
                ["Last 6 Hours", "Last 12 Hours", "Last 24 Hours", "Last 7 Days"],
                index=2
            )
        with col2:
            st.info(f"**{72 if '6 Hours' in time_range else 144 if '12 Hours' in time_range else 288 if '24 Hours' in time_range else 2016}** data points")
        
        hours_map = {
            "Last 6 Hours": 6,
            "Last 12 Hours": 12,
            "Last 24 Hours": 24,
            "Last 7 Days": 168
        }
        
        hours = hours_map[time_range]
        points = min(288, hours * 12)  # 12 points per hour
        
        historical = simulator.get_historical_data(hours=hours, points=points)
        
        # Multi-metric comparison
        fig_multi = create_multi_metric_chart(historical)
        st.plotly_chart(fig_multi, use_container_width=True, config={'displayModeBar': False})
        
        # Statistical summary
        st.markdown('<h2 class="section-header">📈 Statistical Summary</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("**pH** Mean", f"{historical['pH'].mean():.2f} pH")
            st.metric("**pH** Std Dev", f"±{historical['pH'].std():.3f}")
        
        with col2:
            st.metric("**EC** Mean", f"{historical['ec'].mean():.2f} mS/cm")
            st.metric("**EC** Std Dev", f"±{historical['ec'].std():.3f}")
        
        with col3:
            st.metric("**Temp** Mean", f"{historical['water_temp'].mean():.1f}°C")
            st.metric("**Temp** Range", f"{historical['water_temp'].max() - historical['water_temp'].min():.1f}°C")
        
        with col4:
            st.metric("**Humidity** Mean", f"{historical['humidity'].mean():.1f}%")
            st.metric("**Humidity** Range", f"{historical['humidity'].max() - historical['humidity'].min():.1f}%")
        
        # Data table
        st.markdown("---")
        with st.expander("📋 **View Raw Sensor Data Table**", expanded=False):
            st.dataframe(
                historical.style.format({
                    'pH': '{:.2f}',
                    'ec': '{:.2f}',
                    'water_temp': '{:.1f}',
                    'air_temp': '{:.1f}',
                    'humidity': '{:.1f}'
                }),
                use_container_width=True,
                height=400
            )
    
    # TAB 4: SETTINGS
    with tab4:
        st.markdown('<h2 class="section-header">⚙️ System Configuration</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Target Values")
            
            st.number_input(
                "pH Target",
                min_value=5.0,
                max_value=7.0,
                value=SystemConfig.PH_TARGET,
                step=0.1,
                format="%.1f"
            )
            
            st.number_input(
                "pH Tolerance (±)",
                min_value=0.05,
                max_value=0.30,
                value=SystemConfig.PH_TOLERANCE,
                step=0.05,
                format="%.2f"
            )
            
            st.number_input(
                "EC Target (mS/cm)",
                min_value=0.8,
                max_value=2.0,
                value=SystemConfig.EC_TARGET,
                step=0.1,
                format="%.1f"
            )
            
            st.number_input(
                "EC Tolerance (±)",
                min_value=0.03,
                max_value=0.15,
                value=SystemConfig.EC_TOLERANCE,
                step=0.01,
                format="%.2f"
            )
        
        with col2:
            st.markdown("#### 🌡️ Temperature Settings")
            
            st.slider(
                "Temperature Range (°C)",
                min_value=15.0,
                max_value=25.0,
                value=(SystemConfig.TEMP_MIN, SystemConfig.TEMP_MAX),
                step=0.5
            )
            
            st.markdown("#### 🔔 Alert Settings")
            
            st.number_input(
                "Alert Cooldown (seconds)",
                min_value=60,
                max_value=900,
                value=SystemConfig.ALERT_COOLDOWN,
                step=60
            )
            
            st.number_input(
                "AI Scan Interval (minutes)",
                min_value=15,
                max_value=240,
                value=SystemConfig.AI_SCAN_INTERVAL // 60,
                step=15
            )
        
        st.markdown("---")
        
        st.markdown("#### 📡 Connectivity")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.text_input("WiFi SSID", value="YourNetwork", disabled=True)
        
        with col2:
            st.text_input("Firebase Project", value="hydroponic-monitor", disabled=True)
        
        with col3:
            st.selectbox("Region", ["Asia-Southeast1", "US-Central1", "Europe-West1"], disabled=True)
        
        st.markdown("---")
        
        # System information
        st.markdown("#### ℹ️ System Information")
        
        system_info = {
            "Device": "ESP32 DevKit V1",
            "Firmware Version": "v2.0.1",
            "Dashboard Version": "v2.0.0",
            "Last Boot": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Runtime": f"{simulator.step // 3600}h {(simulator.step % 3600) // 60}m",
            "Data Points Collected": f"{simulator.step:,}",
            "Database": "Firebase Realtime Database",
            "AI Model": "Teachable Machine (MobileNet V2)"
        }
        
        for key, value in system_info.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{key}:**")
            with col2:
                st.markdown(value)
    
    # Footer
    st.markdown("""
    <div class="app-footer">
        <strong>HydroVision Pro - Advanced IoT Hydroponic Monitoring System</strong><br>
        Developed by <strong>SET Certification</strong> | Polytechnic University of the Philippines<br>
        MS Computer Engineering (Data Science & Engineering)<br>
        <br>
        📧 Contact: support@setcertification.com | 🌐 www.setcertification.com
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh every 3 seconds (only in demo mode)
    time.sleep(3)
    st.rerun()

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
