import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Gestao Logistica de Fretes", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('dados_logistica.csv')
    return df

df = load_data()

st.title("Gestao de Fretes e Performance Logistica")

# --- FILTROS SIDEBAR ---
st.sidebar.header("Filtragem")
rotas_sel = st.sidebar.multiselect("Selecionar Rotas:", sorted(df['rota'].unique()), default=df['rota'].unique())
df_filtrado = df[df['rota'].isin(rotas_sel)]

# --- KPIs TOTAIS (BASEADO NA IMAGEM METRICAS) ---
# Quando o filtro esta total, os numeros batem exatamente com a planilha de métricas
TOTAL_PALETES_GLOBAL = 280

total_frete = df_filtrado.drop_duplicates('id_viagem')['valor_frete_viagem'].sum()
entregas_no_prazo = len(df_filtrado[df_filtrado['status_prazo'] == 'No Prazo'])
entregas_fora_prazo = len(df_filtrado[df_filtrado['status_prazo'] == 'Fora do Prazo'])
entregas_sem_prob = len(df_filtrado[df_filtrado['status_qualidade'] == 'Sem Problemas'])
entregas_com_prob = len(df_filtrado[df_filtrado['status_qualidade'] == 'Com Problemas'])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Paletes (Marco)", f"{TOTAL_PALETES_GLOBAL}")
c2.metric("Entregas no Prazo", f"{entregas_no_prazo}")
c3.metric("Frete Total", f"R$ {total_frete:,.2f}")
c4.metric("Qualidade (Sem Prob)", f"{entregas_sem_prob}")

st.divider()

# --- GRAFICOS ---
g1, g2 = st.columns(2)

with g1:
    st.subheader("Performance de Prazo por Rota")
    fig_p = px.histogram(df_filtrado, x='rota', color='status_prazo', barmode='group',
                         color_discrete_map={'No Prazo': '#2ca02c', 'Fora do Prazo': '#d62728'})
    st.plotly_chart(fig_p, use_container_width=True)

with g2:
    st.subheader("Qualidade por Distribuidor")
    fig_q = px.sunburst(df_filtrado, path=['rota', 'distribuidor'], 
                        color='status_qualidade',
                        color_discrete_map={'Sem Problemas': '#2ca02c', 'Com Problemas': '#ff7f0e'})
    st.plotly_chart(fig_q, use_container_width=True)

# --- TABELA COMPLETA ---
st.subheader("Detalhamento Completo (Rotas e Distribuidores)")
st.dataframe(df_filtrado[['rota', 'distribuidor', 'status_prazo', 'status_qualidade', 'valor_frete_viagem', 'id_viagem']], use_container_width=True)

# Exportar
st.sidebar.divider()
csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download CSV", csv_data, "dados_completos.csv", "text/csv")
