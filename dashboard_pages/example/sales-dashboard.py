import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Styling
st.markdown("""
    <style>
    .main {
        background-color: #0c111d;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0078d4;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 600;
    }
    .stPlotlyChart {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Generate Mock Data
@st.cache_data
def get_mock_data():
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    n = len(dates)
    
    # Sales Revenue with some seasonality and noise
    base_revenue = 45000 + np.random.normal(0, 5000, n)
    seasonal_revenue = 15000 * np.sin(np.pi * dates.dayofyear / 182)
    revenue = np.maximum(base_revenue + seasonal_revenue, 10000)
    
    # Orders and Users
    orders = (revenue / 250).astype(int)
    users = (orders * 0.8).astype(int)
    
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': revenue,
        'Orders': orders,
        'Active_Users': users,
        'Region': np.random.choice(['North America', 'EMEA', 'APAC', 'LATAM'], n),
        'Product_Category': np.random.choice(['Enterprise Cloud', 'Cyber Security', 'AI Analytics', 'SaaS Core'], n)
    })
    return df

df = get_mock_data()

# Header Section
st.title("📊 Strategic Sales Intelligence")
st.markdown("### Executive Dashboard - Real-time Performance Overview")

# 1. Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rev = df['Revenue'].sum()
    st.metric("Total Revenue", f"${total_rev/1e6:.1f}M", "+12.5%")

with col2:
    total_orders = df['Orders'].sum()
    st.metric("Total Orders", f"{total_orders:,}", "+8.2%")

with col3:
    avg_order = df['Revenue'].mean()
    st.metric("Avg Order Value", f"${avg_order:.2f}", "-1.4%", delta_color="inverse")

with col4:
    conversion_rate = 4.2
    st.metric("Conversion Rate", f"{conversion_rate}%", "+0.5%")

st.divider()

# 2. Main Analytics Row
mid_col1, mid_col2 = st.columns([2, 1])

with mid_col1:
    st.subheader("Revenue Trajectory")
    # Resample to weekly for smoother visualization
    df_weekly = df.set_index('Date').resample('W').sum().reset_index()
    
    fig_line = px.area(df_weekly, x='Date', y='Revenue', 
                       color_discrete_sequence=['#0078d4'],
                       template='plotly_dark')
    fig_line.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    )
    st.plotly_chart(fig_line, use_container_width=True)

with mid_col2:
    st.subheader("Regional Mix")
    region_data = df.groupby('Region')['Revenue'].sum().reset_index()
    fig_pie = px.pie(region_data, values='Revenue', names='Region',
                     hole=0.6,
                     color_discrete_sequence=px.colors.sequential.Blues_r,
                     template='plotly_dark')
    fig_pie.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 3. Product Performance and Filters
st.divider()
bot_col1, bot_col2 = st.columns(2)

with bot_col1:
    st.subheader("Performance by Product Category")
    cat_data = df.groupby('Product_Category')['Revenue'].sum().sort_values(ascending=True).reset_index()
    fig_bar = px.bar(cat_data, y='Product_Category', x='Revenue', 
                     orientation='h',
                     color='Revenue',
                     color_continuous_scale='Blues',
                     template='plotly_dark')
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_title=None,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with bot_col2:
    st.subheader("Key Accounts Intelligence")
    # Fancy Table with mock data
    accounts = pd.DataFrame({
        'Account Name': ['Stark Industries', 'Wayne Corp', 'Cyberdyne', 'Oscorp', 'Umbrella Co'],
        'Contract Value': ['$4.2M', '$3.8M', '$3.1M', '$2.9M', '$2.5M'],
        'Status': ['Renewal', 'Expansion', 'Onboarding', 'Stable', 'At Risk'],
        'Health': [98, 92, 85, 88, 62]
    })
    
    st.dataframe(accounts, 
                 column_config={
                     "Health": st.column_config.ProgressColumn(
                         "Health Score",
                         help="Account health index",
                         format="%d%%",
                         min_value=0,
                         max_value=100,
                     ),
                 },
                 hide_index=True,
                 use_container_width=True)

# Footer
st.markdown("---")
st.caption("Strategic Portfolio Dashboard - Confidencial Management Report - Generated via Streamlit Starterkit")
