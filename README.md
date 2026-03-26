# ⚽ Análise de Odds de Futebol — 1X2

Análise completa de dados de odds 1X2 de futebol europeu, cobrindo **17 ligas** e **2.311 partidas** registradas entre outubro de 2025 e março de 2026.

---

## 📊 O que este projeto explora

- **ETL completo**: limpeza, tipagem, engenharia de features (margem da banca, probabilidade implícita normalizada, volatilidade)
- **Análise Exploratória**: distribuição de odds, volume por liga, perfil de cada mercado
- **Análise Aprofundada**: comportamento temporal das odds, vantagem do mandante, correlações, liquidez de mercado

---

## 🔍 Principais Insights

| # | Insight | Detalhe |
|---|---------|---------|
| 1 | **Margem média da banca: 5,05%** | Serie A é a mais competitiva (4,52%); ligas menores chegam a ~12% |
| 2 | **Odds do mandante caem próximo ao jogo** | Pressão de mercado nas últimas 24h favorece o time da casa |
| 3 | **Vantagem do mandante varia por liga** | Ligas do Leste Europeu apresentam maior desequilíbrio histórico |
| 4 | **Conference League é a mais volátil** | Maior desvio padrão intra-evento — odds oscilam mais durante a semana |
| 5 | **Jogos equilibrados têm maior margem** | Quando favorito e azarão se aproximam em probabilidade, a banca amplia sua margem |
| 6 | **UCL e Premier League têm maior liquidez** | Limites de aposta até 40x superiores a ligas menores |

---

## 📁 Estrutura do projeto

```
odds-analysis/
│
├── notebook.ipynb       # Análise completa com visualizações
├── analysis.py          # Script Python equivalente (standalone)
├── odds1x2.csv          # Dataset original
├── insights.txt         # Resumo dos insights gerados
│
└── img/
    ├── 01_eventos_por_liga.png
    ├── 02_distribuicao_odds.png
    ├── 03_margem_por_liga.png
    ├── 04_movimento_odds_tempo.png
    ├── 05_vantagem_mandante.png
    ├── 06_correlacao.png
    ├── 07_probabilidades_implicitas.png
    ├── 08_volatilidade_liga.png
    ├── 09_favorito_vs_underdog.png
    └── 10_limite_aposta.png
```

---

## 🗃️ Sobre o Dataset

| Campo | Descrição |
|-------|-----------|
| `event_id` | Identificador único da partida |
| `logged_time` | Data/hora do registro da odd |
| `starts` | Data/hora do início da partida |
| `league_name` | Nome da liga |
| `home_team` / `away_team` | Times da partida |
| `home_odds` / `draw_odds` / `away_odds` | Odds 1X2 |
| `max_money_line` | Limite máximo de aposta aceito |

**Features criadas durante o ETL:**

| Feature | Descrição |
|---------|-----------|
| `hours_before_start` | Horas entre o registro e o início do jogo |
| `prob_home/draw/away` | Probabilidade implícita bruta (1/odd) |
| `overround` | Soma das probabilidades brutas (>1 = margem da banca) |
| `margin_pct` | Margem percentual da banca |
| `prob_*_norm` | Probabilidade normalizada (sem margem) |
| `favorite` | Time favorito (home ou away) |
| `fav_prob` | Probabilidade implícita do favorito |
| `underdog_odds` | Odd do azarão |

---

## 🛠️ Como rodar

```bash
# Clone o repositório
git clone https://github.com/lucc4sn/odds-analysis.git
cd odds-analysis

# Instale as dependências
pip install pandas numpy matplotlib seaborn

# Execute o script
python analysis.py

# Ou abra o notebook
jupyter notebook notebook.ipynb
```

---

## 📦 Dependências

```
pandas
numpy
matplotlib
seaborn
jupyter (para o notebook)
```

---

## 👤 Autor

**Luccas Nunes**  
Analista de Social Media & Dados Digitais  
[LinkedIn](https://www.linkedin.com/in/luccas-nunes/) · [GitHub](https://github.com/lucc4sn)
