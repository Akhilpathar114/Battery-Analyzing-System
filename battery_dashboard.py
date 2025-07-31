import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitoring Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []
if 'is_monitoring' not in st.session_state:
    st.session_state.is_monitoring = False

# Cell type configurations
CELL_CONFIGS = {
    "LFP": {
        "nominal_voltage": 3.2,
        "min_voltage": 2.8,
        "max_voltage": 3.6,
        "color": "#2ecc71"
    },
    "NMC": {
        "nominal_voltage": 3.6,
        "min_voltage": 3.2,
        "max_voltage": 4.0,
        "color": "#e74c3c"
    },
    "LTO": {
        "nominal_voltage": 2.4,
        "min_voltage": 1.5,
        "max_voltage": 2.8,
        "color": "#f39c12"
    },
    "LiCoO2": {
        "nominal_voltage": 3.7,
        "min_voltage": 3.0,
        "max_voltage": 4.2,
        "color": "#9b59b6"
    }
}

def generate_cell_data(cell_type, cell_id, current_time):
    """Generate realistic battery cell data"""
    config = CELL_CONFIGS[cell_type]
    
    # Simulate realistic voltage fluctuations
    base_voltage = config["nominal_voltage"]
    voltage_variation = random.uniform(-0.1, 0.1)
    voltage = round(base_voltage + voltage_variation, 3)
    
    # Simulate current (positive for charging, negative for discharging)
    current = round(random.uniform(-5.0, 5.0), 2)
    
    # Temperature simulation with some correlation to current
    base_temp = 25
    temp_variation = abs(current) * 0.5 + random.uniform(-2, 8)
    temperature = round(base_temp + temp_variation, 1)
    
    # Calculate power and capacity
    power = round(voltage * abs(current), 2)
    capacity = round(random.uniform(2.8, 3.2), 2)  # Ah
    
    # Health calculation based on voltage and temperature
    voltage_health = 100 * (1 - abs(voltage - config["nominal_voltage"]) / config["nominal_voltage"])
    temp_health = 100 * max(0, 1 - max(0, temperature - 35) / 20)
    overall_health = round((voltage_health + temp_health) / 2, 1)
    
    # Status determination
    if voltage < config["min_voltage"] or voltage > config["max_voltage"] or temperature > 45:
        status = "Critical"
    elif temperature > 40 or overall_health < 80:
        status = "Warning"
    else:
        status = "Good"
    
    return {
        "cell_id": cell_id,
        "cell_type": cell_type,
        "voltage": voltage,
        "current": current,
        "temperature": temperature,
        "power": power,
        "capacity": capacity,
        "health": overall_health,
        "status": status,
        "timestamp": current_time,
        "min_voltage": config["min_voltage"],
        "max_voltage": config["max_voltage"]
    }

def get_status_color(status):
    """Return color based on status"""
    if status == "Good":
        return "status-good"
    elif status == "Warning":
        return "status-warning"
    else:
        return "status-critical"

# Main Dashboard
st.markdown('<h1 class="main-header">🔋 Battery Cell Monitoring Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Bench and group information
    bench_name = st.text_input("Bench Name", value="Bench-001", key="bench_name")
    group_num = st.number_input("Group Number", min_value=1, max_value=100, value=1, key="group_num")
    
    st.divider()
    
    # Cell configuration
    st.subheader("Cell Configuration")
    num_cells = st.slider("Number of Cells", min_value=1, max_value=16, value=8)
    
    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell {i+1} Type",
            options=list(CELL_CONFIGS.keys()),
            key=f"cell_type_{i}"
        )
        cell_types.append(cell_type)
    
    st.divider()
    
    # Control panel
    st.subheader("🎛️ Control Panel")
    
    if st.button("Initialize Cells", type="primary"):
        current_time = datetime.now()
        st.session_state.cells_data = {}
        for i, cell_type in enumerate(cell_types):
            cell_id = f"Cell_{i+1}_{cell_type}"
            st.session_state.cells_data[cell_id] = generate_cell_data(cell_type, cell_id, current_time)
        st.success("Cells initialized successfully!")
    
    # Monitoring controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Monitoring"):
            st.session_state.is_monitoring = True
            st.success("Monitoring started!")
    
    with col2:
        if st.button("Stop Monitoring"):
            st.session_state.is_monitoring = False
            st.info("Monitoring stopped!")
    
    # Auto-refresh
    auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
    
    if auto_refresh and st.session_state.is_monitoring:
        time.sleep(5)
        st.rerun()

# Main content area
if st.session_state.cells_data:
    
    # Update data if monitoring
    if st.session_state.is_monitoring:
        current_time = datetime.now()
        for cell_id in st.session_state.cells_data.keys():
            cell_type = st.session_state.cells_data[cell_id]["cell_type"]
            st.session_state.cells_data[cell_id] = generate_cell_data(cell_type, cell_id, current_time)
        
        # Store historical data
        st.session_state.historical_data.append({
            "timestamp": current_time,
            "data": st.session_state.cells_data.copy()
        })
        
        # Keep only last 100 records
        if len(st.session_state.historical_data) > 100:
            st.session_state.historical_data = st.session_state.historical_data[-100:]
    
    # System overview
    st.header(f"📊 System Overview - {bench_name} (Group {group_num})")
    
    # Summary metrics
    total_cells = len(st.session_state.cells_data)
    good_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Good")
    warning_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Warning")
    critical_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Critical")
    avg_health = np.mean([cell["health"] for cell in st.session_state.cells_data.values()])
    total_power = sum([cell["power"] for cell in st.session_state.cells_data.values()])
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Cells", total_cells)
    with col2:
        st.metric("Good Cells", good_cells, delta=None)
    with col3:
        st.metric("Warning Cells", warning_cells, delta=None)
    with col4:
        st.metric("Critical Cells", critical_cells, delta=None)
    with col5:
        st.metric("Avg Health", f"{avg_health:.1f}%")
    with col6:
        st.metric("Total Power", f"{total_power:.2f}W")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Real-time Data", "📊 Cell Health", "🔥 Temperature Monitor", "⚡ Historical Trends"])
    
    with tab1:
        st.subheader("Real-time Cell Data")
        
        # Create DataFrame for display
        df = pd.DataFrame(st.session_state.cells_data.values())
        
        # Display data table
        st.dataframe(
            df[["cell_id", "cell_type", "voltage", "current", "temperature", "power", "capacity", "health", "status"]],
            use_container_width=True
        )
        
        # Voltage comparison chart
        fig_voltage = px.bar(
            df, 
            x="cell_id", 
            y="voltage", 
            color="cell_type",
            title="Cell Voltage Comparison",
            color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
        )
        fig_voltage.add_hline(y=df["min_voltage"].iloc[0], line_dash="dash", line_color="red", annotation_text="Min Voltage")
        fig_voltage.add_hline(y=df["max_voltage"].iloc[0], line_dash="dash", line_color="red", annotation_text="Max Voltage")
        st.plotly_chart(fig_voltage, use_container_width=True)
    
    with tab2:
        st.subheader("Cell Health Analysis")
        
        # Health gauge charts
        cols = st.columns(4)
        for i, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[i % 4]:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = cell_data["health"],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': cell_id},
                    delta = {'reference': 100},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_gauge.update_layout(height=250)
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Health distribution
        fig_health = px.histogram(
            df, 
            x="health", 
            nbins=10, 
            title="Health Distribution",
            color="status",
            color_discrete_map={"Good": "green", "Warning": "orange", "Critical": "red"}
        )
        st.plotly_chart(fig_health, use_container_width=True)
    
    with tab3:
        st.subheader("Temperature Monitoring")
        
        # Temperature heatmap
        temp_data = df.pivot_table(values='temperature', index='cell_type', columns='cell_id', fill_value=0)
        fig_temp = px.imshow(
            temp_data, 
            title="Temperature Heatmap",
            color_continuous_scale="RdYlBu_r",
            aspect="auto"
        )
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Temperature vs Power scatter
        fig_scatter = px.scatter(
            df, 
            x="temperature", 
            y="power", 
            color="cell_type",
            size="health",
            title="Temperature vs Power Analysis",
            hover_data=["cell_id", "voltage", "current"]
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.subheader("Historical Trends")
        
        if len(st.session_state.historical_data) > 1:
            # Prepare historical data
            hist_df = []
            for record in st.session_state.historical_data[-50:]:  # Last 50 records
                for cell_id, cell_data in record["data"].items():
                    hist_df.append({
                        "timestamp": record["timestamp"],
                        "cell_id": cell_id,
                        "voltage": cell_data["voltage"],
                        "current": cell_data["current"],
                        "temperature": cell_data["temperature"],
                        "health": cell_data["health"]
                    })
            
            hist_df = pd.DataFrame(hist_df)
            
            # Multi-line charts
            fig_trends = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Voltage Trends", "Current Trends", "Temperature Trends", "Health Trends"),
                vertical_spacing=0.08
            )
            
            # Voltage trends
            for cell_id in hist_df["cell_id"].unique():
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(x=cell_hist["timestamp"], y=cell_hist["voltage"], name=f"{cell_id}_V", line=dict(width=2)),
                    row=1, col=1
                )
            
            # Current trends
            for cell_id in hist_df["cell_id"].unique():
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(x=cell_hist["timestamp"], y=cell_hist["current"], name=f"{cell_id}_I", showlegend=False),
                    row=1, col=2
                )
            
            # Temperature trends
            for cell_id in hist_df["cell_id"].unique():
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(x=cell_hist["timestamp"], y=cell_hist["temperature"], name=f"{cell_id}_T", showlegend=False),
                    row=2, col=1
                )
            
            # Health trends
            for cell_id in hist_df["cell_id"].unique():
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(x=cell_hist["timestamp"], y=cell_hist["health"], name=f"{cell_id}_H", showlegend=False),
                    row=2, col=2
                )
            
            fig_trends.update_layout(height=600, title_text="Historical Data Trends")
            fig_trends.update_xaxes(title_text="Time")
            fig_trends.update_yaxes(title_text="Voltage (V)", row=1, col=1)
            fig_trends.update_yaxes(title_text="Current (A)", row=1, col=2)
            fig_trends.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
            fig_trends.update_yaxes(title_text="Health (%)", row=2, col=2)
            
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("Start monitoring to see historical trends...")

else:
    st.info("👈 Please configure and initialize cells using the sidebar to begin monitoring.")
    
    # Display sample configuration
    st.subheader("Sample Cell Types Available:")
    for cell_type, config in CELL_CONFIGS.items():
        st.write(f"**{cell_type}**: {config['min_voltage']}V - {config['max_voltage']}V (Nominal: {config['nominal_voltage']}V)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Battery Cell Monitoring Dashboard | Real-time monitoring and analysis</p>
    </div>
    """, 
    unsafe_allow_html=True
)