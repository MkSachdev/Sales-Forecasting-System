import plotly.graph_objects as go
import streamlit as st

from src.data_loader import (
    load_forecast_sales,
    load_historical_sales,
    weekly_sales_for_state,
)


st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --bg: #080b12;
        --panel: #111827;
        --panel-soft: #162033;
        --text: #f8fafc;
        --muted: #94a3b8;
        --accent: #22d3ee;
        --accent-2: #f59e0b;
        --border: rgba(148, 163, 184, 0.18);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34, 211, 238, 0.12), transparent 32rem),
            linear-gradient(135deg, #080b12 0%, #101624 55%, #0b1020 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: rgba(8, 11, 18, 0.88);
        border-right: 1px solid var(--border);
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1280px;
    }

    .dashboard-header {
        padding: 0 0 0.65rem;
    }

    .dashboard-header h1 {
        color: var(--text);
        font-size: 1.9rem;
        line-height: 1.1;
        margin: 0;
        letter-spacing: 0;
    }

    .dashboard-header p {
        color: var(--muted);
        font-size: 0.92rem;
        margin: 0.35rem 0 0;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.96), rgba(22, 32, 51, 0.92));
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.8rem 0.95rem;
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.24);
        min-height: 96px;
    }

    .metric-card .label {
        color: var(--muted);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .metric-card .value {
        color: var(--text);
        font-size: clamp(1.15rem, 1.8vw, 1.65rem);
        font-weight: 800;
        letter-spacing: 0;
        white-space: nowrap;
    }

    .metric-card .caption {
        color: var(--muted);
        font-size: 0.76rem;
        margin-top: 0.3rem;
    }

    div[data-testid="stPlotlyChart"] {
        background: rgba(17, 24, 39, 0.66);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.35rem;
    }

    .section-title {
        color: var(--text);
        font-size: 0.96rem;
        font-weight: 800;
        margin: 0.75rem 0 0.45rem;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    div[data-testid="stExpander"] {
        background: rgba(17, 24, 39, 0.52);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def get_data():
    return load_historical_sales(), load_forecast_sales()


def format_currency(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:,.0f}"


def build_historical_chart(weekly_df):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weekly_df["Date"],
            y=weekly_df["Sales"],
            mode="lines",
            name="Historical Sales",
            line=dict(color="#22d3ee", width=3),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=330,
        margin=dict(l=14, r=14, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8, 11, 18, 0.36)",
        font=dict(color="#e5e7eb", family="Inter, Arial, sans-serif"),
        hovermode="x unified",
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(
            title=None,
            gridcolor="rgba(148, 163, 184, 0.14)",
            tickprefix="$",
            separatethousands=True,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def build_forecast_chart(forecast_df):
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=forecast_df["Week"],
            y=forecast_df["Forecasted_Sales"],
            name="Forecasted Sales",
            marker=dict(
                color=forecast_df["Forecasted_Sales"],
                colorscale=[[0, "#0f766e"], [1, "#f59e0b"]],
                line=dict(color="rgba(255,255,255,0.18)", width=1),
            ),
            hovertemplate="<b>%{x}</b><br>Forecast: $%{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=330,
        margin=dict(l=14, r=14, t=12, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8, 11, 18, 0.36)",
        font=dict(color="#e5e7eb", family="Inter, Arial, sans-serif"),
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(
            title=None,
            gridcolor="rgba(148, 163, 184, 0.14)",
            tickprefix="$",
            separatethousands=True,
        ),
        showlegend=False,
    )
    return fig


historical_df, forecast_df = get_data()
states = sorted(set(historical_df["State"]).intersection(forecast_df["State"]))

with st.sidebar:
    st.title("Controls")
    selected_state = st.selectbox("Select State", states, index=states.index("California") if "California" in states else 0)
    st.caption("Forecast values are loaded from the existing generated forecast file.")

state_weekly_sales = weekly_sales_for_state(historical_df, selected_state)
state_forecast = forecast_df[forecast_df["State"] == selected_state].copy()

total_sales = state_weekly_sales["Sales"].sum()
average_sales = state_weekly_sales["Sales"].mean()
forecasted_sales = state_forecast["Forecasted_Sales"].sum()
last_actual_date = state_weekly_sales["Date"].max()

st.markdown(
    f"""
    <div class="dashboard-header">
        <h1>Sales Forecasting Dashboard</h1>
        <p>Portfolio-ready view of historical sales performance and the next 8 forecasted weeks for <strong>{selected_state}</strong>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">Total Sales</div>
            <div class="value">{format_currency(total_sales)}</div>
            <div class="caption">Historical weekly sales through {last_actual_date:%b %d, %Y}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">Average Sales</div>
            <div class="value">{format_currency(average_sales)}</div>
            <div class="caption">Average weekly historical sales</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">Forecasted Sales</div>
            <div class="value">{format_currency(forecasted_sales)}</div>
            <div class="caption">Projected total across the next 8 weeks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

left, right = st.columns(2)
with left:
    st.markdown('<div class="section-title">Historical Sales Trend</div>', unsafe_allow_html=True)
    st.plotly_chart(build_historical_chart(state_weekly_sales), width="stretch")

with right:
    st.markdown('<div class="section-title">8-Week Sales Forecast</div>', unsafe_allow_html=True)
    st.plotly_chart(build_forecast_chart(state_forecast), width="stretch")

st.markdown('<div class="section-title">Forecast Table</div>', unsafe_allow_html=True)
with st.expander("View forecast data table"):
    st.dataframe(
        state_forecast[["Week", "Forecasted_Sales"]].rename(
            columns={"Week": "Forecast Week", "Forecasted_Sales": "Forecasted Sales"}
        ),
        width="stretch",
        hide_index=True,
    )
