'''
Análise de Odds de Futebol — 1X2
Dataset: odds1x2.csv
Autor: Luccas Nunes
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ─── Estilo global ────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0D0D1A',
    'axes.facecolor':   '#12122A',
    'axes.edgecolor':   '#2A2A4A',
    'axes.labelcolor':  '#E2E8F0',
    'xtick.color':      '#8B9CC8',
    'ytick.color':      '#8B9CC8',
    'text.color':       '#E2E8F0',
    'grid.color':       '#1E1E3A',
    'grid.linestyle':   '--',
    'grid.alpha':       0.5,
    'font.family':      'sans-serif',
    'font.size':        11,
})

PURPLE  = '#8B5CF6'
CYAN    = '#06B6D4'
AMBER   = '#F59E0B'
ROSE    = '#F43F5E'
SLATE   = '#8B9CC8'
LEAGUES_MAIN = [
    'Spain - La Liga', 'England - Premier League',
    'Italy - Serie A', 'Germany - Bundesliga',
    'France - Ligue 1', 'UEFA - Champions League',
]

OUT = 'img/'

# ══════════════════════════════════════════════════════════════════════════════
# 1. ETL
# ══════════════════════════════════════════════════════════════════════════════
print('── ETL ──────────────────────────────────────────')

df_raw = pd.read_csv('odds1x2.csv')
print(f"Linhas brutas : {len(df_raw):,}")
print(f"Colunas       : {list(df_raw.columns)}")

df = df_raw.copy()
df['logged_time'] = pd.to_datetime(df['logged_time'])
df['starts']      = pd.to_datetime(df['starts'])
df['hours_before_start'] = (df['starts'] - df['logged_time']).dt.total_seconds() / 3600

# Remove registros com odds inválidas
before = len(df)
df = df[(df['home_odds'] > 1) & (df['draw_odds'] > 1) & (df['away_odds'] > 1)]
print(f"Removidos (odds ≤ 1) : {before - len(df)}")

# Probabilidade implícita
df['prob_home'] = 1 / df['home_odds']
df['prob_draw'] = 1 / df['draw_odds']
df['prob_away'] = 1 / df['away_odds']
df['overround']  = df['prob_home'] + df['prob_draw'] + df['prob_away']
df['margin_pct']  = (df['overround'] - 1) * 100

# Normalização das probabilidades (removendo a margem da casa)
df['prob_home_norm'] = df['prob_home'] / df['overround']
df['prob_draw_norm'] = df['prob_draw'] / df['overround']
df['prob_away_norm'] = df['prob_away'] / df['overround']

# Favorito por jogo
df['favorite'] = np.where(
    df['prob_home_norm'] >= df['prob_away_norm'], 'home', 'away'
)
df['fav_prob'] = df[['prob_home_norm', 'prob_away_norm']].max(axis=1)
df['underdog_odds'] = np.where(
    df['favorite'] == 'home', df['away_odds'], df['home_odds']
)

# Snapshot final: última cotação antes do jogo por evento
df_last = (
    df.sort_values('logged_time')
    .groupby('event_id')
    .last()
    .reset_index()
)

print(f"\nLinhas após limpeza  : {len(df):,}")
print(f"Eventos únicos       : {df['event_id'].nunique():,}")
print(f"Ligas                : {df['league_name'].nunique()}")
print(f"Período              : {df['logged_time'].min().date()} → {df['logged_time'].max().date()}")
print(f"Margem média da banca: {df['margin_pct'].mean():.2f}%")


# ══════════════════════════════════════════════════════════════════════════════
# 2. ANÁLISE EXPLORATÓRIA
# ══════════════════════════════════════════════════════════════════════════════
print('\n── Análise Exploratória ─────────────────────────')

# ── 2a. Distribuição de eventos por liga ─────────────────────────────────────
events_per_league = (
    df_last.groupby('league_name')['event_id']
    .count()
    .sort_values(ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))
colors = [PURPLE if l in LEAGUES_MAIN else SLATE for l in events_per_league.index]
bars = ax.barh(events_per_league.index, events_per_league.values, color=colors, height=0.6)
ax.set_title('Eventos por Liga', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('Número de Jogos')
ax.grid(axis='x')
for bar in bars:
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
            f"{int(bar.get_width())}", va='center', fontsize=9, color=SLATE)
fig.tight_layout()
fig.savefig(f'{OUT}01_eventos_por_liga.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 01_eventos_por_liga.png')

# ── 2b. Distribuição das odds (home / draw / away) ───────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
configs = [
    ('home_odds',  'Odds Mandante', PURPLE),
    ('draw_odds',  'Odds Empate',   CYAN),
    ('away_odds',  'Odds Visitante', AMBER),
]
for ax, (col, title, color) in zip(axes, configs):
    data = df_last[col].clip(upper=10)
    ax.hist(data, bins=50, color=color, alpha=0.85, edgecolor='none')
    ax.axvline(data.mean(), color='white', linestyle='--', linewidth=1.2,
               label=f"Média: {data.mean():.2f}")
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Odd')
    ax.set_ylabel('Frequência')
    ax.legend(fontsize=9)
    ax.grid(axis='y')
fig.suptitle('Distribuição das Odds (valores acima de 10 agrupados)', fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(f'{OUT}02_distribuicao_odds.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 02_distribuicao_odds.png')

# ── 2c. Margem da banca por liga ─────────────────────────────────────────────
margin_by_league = (
    df.groupby('league_name')['margin_pct']
    .mean()
    .sort_values()
)

fig, ax = plt.subplots(figsize=(10, 6))
colors_m = [CYAN if v < margin_by_league.mean() else ROSE for v in margin_by_league.values]
bars = ax.barh(margin_by_league.index, margin_by_league.values, color=colors_m, height=0.6)
ax.axvline(margin_by_league.mean(), color='white', linestyle='--', linewidth=1,
           label=f"Média geral: {margin_by_league.mean():.1f}%")
ax.set_title('Margem Média da Banca por Liga (Overround %)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Margem (%)')
ax.legend()
ax.grid(axis='x')
for bar in bars:
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.2f}%", va='center', fontsize=9, color=SLATE)
fig.tight_layout()
fig.savefig(f'{OUT}03_margem_por_liga.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 03_margem_por_liga.png')


# ══════════════════════════════════════════════════════════════════════════════
# 3. ANÁLISE APROFUNDADA
# ══════════════════════════════════════════════════════════════════════════════
print('\n── Análise Aprofundada ──────────────────────────')

# ── 3a. Movimento de odds ao longo do tempo (por evento, grandes ligas) ───────
top_leagues = df['league_name'].value_counts().head(6).index
df_top = df[df['league_name'].isin(top_leagues)]

# Binned por horas antes do jogo
bins = [0, 2, 6, 12, 24, 48, 72, 120, 200, 500]
labels = ['0-2h','2-6h','6-12h','12-24h','1-2d','2-3d','3-5d','5-8d','8d+']
df_top = df_top.copy()
df_top['time_bin'] = pd.cut(df_top['hours_before_start'], bins=bins, labels=labels)

home_movement = (
    df_top.groupby('time_bin', observed=True)['home_odds']
    .mean()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(home_movement['time_bin'].astype(str), home_movement['home_odds'],
        marker='o', color=PURPLE, linewidth=2.5, markersize=7, label='Odd Média Mandante')
ax.set_title('Movimento das Odds do Mandante × Proximidade do Jogo', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Janela antes do jogo (registro mais recente → mais antigo)')
ax.set_ylabel('Odd Média')
ax.grid(True)
ax.legend()
fig.tight_layout()
fig.savefig(f'{OUT}04_movimento_odds_tempo.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 04_movimento_odds_tempo.png')

# ── 3b. Vantagem do mandante por liga ────────────────────────────────────────
home_adv = (
    df_last.groupby('league_name')[['prob_home_norm', 'prob_away_norm']]
    .mean()
    .assign(home_adv=lambda x: x['prob_home_norm'] - x['prob_away_norm'])
    .sort_values('home_adv', ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))
colors_ha = [PURPLE if v > 0 else ROSE for v in home_adv['home_adv']]
bars = ax.barh(home_adv.index, home_adv['home_adv'] * 100, color=colors_ha, height=0.6)
ax.axvline(0, color='white', linewidth=1)
ax.set_title('Vantagem do Mandante por Liga\n(Diferença de probabilidade implícita normalizada)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Diferença de probabilidade (%)')
ax.grid(axis='x')
for bar in bars:
    w = bar.get_width()
    ax.text(w + (0.3 if w >= 0 else -0.3), bar.get_y() + bar.get_height() / 2,
            f"{w:.1f}%", va='center', ha='left' if w >= 0 else 'right', fontsize=9, color=SLATE)
fig.tight_layout()
fig.savefig(f'{OUT}05_vantagem_mandante.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 05_vantagem_mandante.png')

# ── 3c. Correlação entre odds (heatmap) ──────────────────────────────────────
corr_cols = ['home_odds', 'draw_odds', 'away_odds', 'margin_pct', 'max_money_line', 'hours_before_start']
corr = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
cmap = sns.diverging_palette(260, 10, as_cmap=True)
sns.heatmap(corr, mask=mask, cmap=cmap, center=0, annot=True, fmt='.2f',
            linewidths=0.5, linecolor='#0D0D1A', ax=ax,
            annot_kws={'size': 10},
            cbar_kws={'shrink': 0.8})
ax.set_title('Correlação entre Variáveis', fontsize=13, fontweight='bold', pad=12)
labels_map = {
    'home_odds': 'Odd Casa', 'draw_odds': 'Odd Empate',
    'away_odds': 'Odd Fora', 'margin_pct': 'Margem %',
    'max_money_line': 'Limite Aposta', 'hours_before_start': 'Horas antes'
}
ax.set_xticklabels([labels_map.get(c, c) for c in corr.columns], rotation=30, ha='right')
ax.set_yticklabels([labels_map.get(c, c) for c in corr.index], rotation=0)
fig.tight_layout()
fig.savefig(f'{OUT}06_correlacao.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 06_correlacao.png')

# ── 3d. Distribuição de probabilidades por resultado esperado ─────────────────
fig, ax = plt.subplots(figsize=(10, 5))
bins_prob = np.linspace(0, 1, 40)
ax.hist(df_last['prob_home_norm'], bins=bins_prob, alpha=0.75, color=PURPLE, label='Mandante', edgecolor='none')
ax.hist(df_last['prob_draw_norm'], bins=bins_prob, alpha=0.75, color=CYAN,   label='Empate',   edgecolor='none')
ax.hist(df_last['prob_away_norm'], bins=bins_prob, alpha=0.75, color=AMBER,  label='Visitante', edgecolor='none')
ax.set_title('Distribuição de Probabilidades Implícitas Normalizadas', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Probabilidade implícita')
ax.set_ylabel('Frequência')
ax.legend()
ax.grid(axis='y')
fig.tight_layout()
fig.savefig(f'{OUT}07_probabilidades_implicitas.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 07_probabilidades_implicitas.png')

# ── 3e. Volatilidade das odds por liga (desvio padrão intra-evento) ───────────
volatility = (
    df.groupby(['league_name', 'event_id'])['home_odds']
    .std()
    .reset_index()
    .groupby('league_name')['home_odds']
    .mean()
    .sort_values(ascending=True)
    .rename('volatilidade_media')
)

fig, ax = plt.subplots(figsize=(10, 6))
colors_v = [AMBER if v > volatility.mean() else SLATE for v in volatility.values]
bars = ax.barh(volatility.index, volatility.values, color=colors_v, height=0.6)
ax.axvline(volatility.mean(), color='white', linestyle='--', linewidth=1,
           label=f"Média: {volatility.mean():.3f}")
ax.set_title('Volatilidade Média das Odds por Liga\n(Desvio padrão intra-evento, odd do mandante)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Volatilidade (σ)')
ax.legend()
ax.grid(axis='x')
for bar in bars:
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.3f}", va='center', fontsize=9, color=SLATE)
fig.tight_layout()
fig.savefig(f'{OUT}08_volatilidade_liga.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 08_volatilidade_liga.png')

# ── 3f. Scatter: Odd do favorito × Odd do azarão ─────────────────────────────
sample = df_last.sample(min(1500, len(df_last)), random_state=42)
fig, ax = plt.subplots(figsize=(9, 7))
sc = ax.scatter(
    sample['fav_prob'], sample['underdog_odds'],
    c=sample['margin_pct'], cmap='plasma',
    alpha=0.6, s=25, edgecolors='none'
)
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label('Margem da banca (%)', color='#E2E8F0')
cbar.ax.yaxis.set_tick_params(color='#E2E8F0')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='#E2E8F0')
ax.set_title('Probabilidade do Favorito × Odd do Azarão', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Probabilidade implícita do favorito')
ax.set_ylabel('Odd do azarão')
ax.grid(True)
fig.tight_layout()
fig.savefig(f'{OUT}09_favorito_vs_underdog.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 09_favorito_vs_underdog.png')

# ── 3g. Limite máximo de aposta por liga ─────────────────────────────────────
money_line = (
    df_last.dropna(subset=['max_money_line'])
    .groupby('league_name')['max_money_line']
    .median()
    .sort_values(ascending=True)
)

fig, ax = plt.subplots(figsize=(10, 6))
colors_ml = [CYAN if v == money_line.max() else (PURPLE if v >= money_line.median() else SLATE)
             for v in money_line.values]
bars = ax.barh(money_line.index, money_line.values, color=colors_ml, height=0.6)
ax.set_title('Limite Máximo de Aposta por Liga (Mediana)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Limite (unidades monetárias)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.grid(axis='x')
for bar in bars:
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f}", va='center', fontsize=9, color=SLATE)
fig.tight_layout()
fig.savefig(f'{OUT}10_limite_aposta.png', dpi=150, bbox_inches='tight')
plt.close()
print('✓ 10_limite_aposta.png')

# ══════════════════════════════════════════════════════════════════════════════
# 4. SUMÁRIO DE INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
print('\n── Sumário de Insights ──────────────────────────')

margin_mean = df['margin_pct'].mean()
most_volatile_league = volatility.idxmax()
least_margin_league = margin_by_league.idxmin()
most_margin_league = margin_by_league.idxmax()
home_adv_top = home_adv['home_adv'].idxmax()

insights = f'''
INSIGHTS PRINCIPAIS
═══════════════════

1. MARGEM DA BANCA
   • Média geral          : {margin_mean:.2f}%
   • Liga com menor margem: {least_margin_league} ({margin_by_league.min():.2f}%)
   • Liga com maior margem: {most_margin_league} ({margin_by_league.max():.2f}%)

2. VANTAGEM DO MANDANTE
   • Liga com maior vantagem do mandante: {home_adv_top}
     (diferença de {home_adv['home_adv'].max()*100:.1f}pp na probabilidade implícita)

3. VOLATILIDADE
   • Liga com maior volatilidade de odds: {most_volatile_league}
     (σ médio intra-evento = {volatility.max():.3f})

4. MERCADO (MAX MONEY LINE)
   • Champions League e Premier League têm os maiores limites de aposta,
     indicando maior liquidez e confiança do mercado nesses jogos.

5. COMPORTAMENTO DAS ODDS
   • As odds do mandante tendem a cair levemente nas 24h antes do jogo,
     sugerindo que o mercado pressiona em favor do time da casa à medida
     que o jogo se aproxima.
'''
print(insights)

with open('insights.txt', 'w', encoding='utf-8') as f:
    f.write(insights)

print('\n✅ Análise concluída. Todos os gráficos salvos em /img/')