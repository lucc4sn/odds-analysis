import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Football Odds Analytics", layout="wide", initial_sidebar_state="expanded")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #0D0D1A; color: #E2E8F0; }
    .stMetric { background-color: #12122A; border: 1px solid #2A2A4A; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS (CACHE) ---
@st.cache_data
def load_data():
    df = pd.read_csv('odds1x2.csv')
    df['logged_time'] = pd.to_datetime(df['logged_time'])
    df['starts'] = pd.to_datetime(df['starts'])
    df['hours_before_start'] = (df['starts'] - df['logged_time']).dt.total_seconds() / 3600
    df = df[(df['home_odds'] > 1) & (df['draw_odds'] > 1) & (df['away_odds'] > 1)]
    
    # Cálculos
    df['prob_home'] = 1 / df['home_odds']
    df['prob_draw'] = 1 / df['draw_odds']
    df['prob_away'] = 1 / df['away_odds']
    df['overround'] = df['prob_home'] + df['prob_draw'] + df['prob_away']
    df['margin_pct'] = (df['overround'] - 1) * 100
    
    # Normalização
    df['prob_home_norm'] = df['prob_home'] / df['overround']
    df['prob_draw_norm'] = df['prob_draw'] / df['overround']
    df['prob_away_norm'] = df['prob_away'] / df['overround']
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Arquivo 'odds1x2.csv' não encontrado!")
    st.stop()

# --- SIDEBAR / FILTROS ---
st.sidebar.title("⚽ Filtros de Análise")
leagues = st.sidebar.multiselect("Selecione as Ligas", 
                                 options=df['league_name'].unique(), 
                                 default=df['league_name'].unique()[:5])

filtered_df = df[df['league_name'].isin(leagues)]
df_last = filtered_df.sort_values('logged_time').groupby('event_id').last().reset_index()

# --- DASHBOARD ---
st.title("📊 Dashboard de Odds 1X2")
st.markdown("---")

# Métricas Principais
m1, m2, m3, m4 = st.columns(4)
m1.metric("Eventos Únicos", f"{df_last.shape[0]}")
m2.metric("Margem Média", f"{filtered_df['margin_pct'].mean():.2f}%")
m3.metric("Maior Limite (Mediana)", f"{df_last['max_money_line'].median():,.0f}")
m4.metric("Ligas Selecionadas", len(leagues))

st.markdown("---")

# Layout de Colunas para Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏦 Margem da Banca por Liga")
    margin_fig = px.bar(
        df_last.groupby('league_name')['margin_pct'].mean().sort_values(),
        orientation='h',
        color_discrete_sequence=['#06B6D4'],
        labels={'value': 'Margem %', 'league_name': 'Liga'}
    )
    margin_fig.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(margin_fig, use_container_width=True)

with col2:
    st.subheader("🏠 Vantagem do Mandante (%)")
    # Diferença de prob mandante vs visitante
    ha = df_last.groupby('league_name').apply(lambda x: (x['prob_home_norm'] - x['prob_away_norm']).mean() * 100).sort_values()
    ha_fig = px.bar(ha, orientation='h', color=ha.values, 
                    color_continuous_scale='RdBu', labels={'value': 'Vantagem (%)'})
    ha_fig.update_layout(template="plotly_dark")
    st.plotly_chart(ha_fig, use_container_width=True)

# Linha 2 de Gráficos
st.markdown("---")
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader("📈 Movimentação de Odds (Horas antes do jogo)")
    # Slider para filtrar janela de tempo no gráfico
    window = st.slider("Janela de Horas", 0, 100, (0, 48))
    temp_df = filtered_df[(filtered_df['hours_before_start'] >= window[0]) & (filtered_df['hours_before_start'] <= window[1])]
    
    line_fig = px.line(
        temp_df.groupby('hours_before_start')['home_odds'].mean().reset_index(),
        x='hours_before_start', y='home_odds',
        title="Média de Odds Mandante vs. Proximidade",
        color_discrete_sequence=['#8B5CF6']
    )
    line_fig.update_xaxes(autorange="reversed") # O jogo está no zero
    line_fig.update_layout(template="plotly_dark")
    st.plotly_chart(line_fig, use_container_width=True)

with col4:
    st.subheader("🎯 Distribuição de Resultados")
    dist_data = df_last[['prob_home_norm', 'prob_draw_norm', 'prob_away_norm']].mean()
    pie_fig = px.pie(
        names=['Mandante', 'Empate', 'Visitante'],
        values=dist_data.values,
        color_discrete_sequence=['#8B5CF6', '#06B6D4', '#F59E0B'],
        hole=0.4
    )
    pie_fig.update_layout(template="plotly_dark")
    st.plotly_chart(pie_fig, use_container_width=True)

# Tabela de Dados Brutos (Opcional)
if st.checkbox("Mostrar dados filtrados"):
    st.dataframe(df_last.style.background_gradient(subset=['margin_pct'], cmap='YlOrRd'))