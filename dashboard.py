import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(page_title="Dashboard Logística - Acompanhamento", layout="wide")

st.title("📊 Acompanhamento de Métricas Logísticas")
st.markdown("Dashboard alimentado semanalmente via arquivo CSV.")

# Carregar Dados
@st.cache_data
def load_data():
    df = pd.read_csv('dados_logistica.csv')
    df['data_referencia'] = pd.to_datetime(df['data_referencia'])
    return df

df = load_data()

# Filtros Lateral
st.sidebar.header("Filtros")
meses = df['data_referencia'].dt.strftime('%B %Y').unique()
mes_selecionado = st.sidebar.multiselect("Selecione o Mês:", meses, default=meses)

# Filtragem de Dados
df_filtrado = df[df['data_referencia'].dt.strftime('%B %Y').isin(mes_selecionado)]

# --- KPIs PRINCIPAIS ---
col1, col2, col3, col4 = st.columns(4)

# 1. TEMPO (SLA de Entrega)
sla = (df_filtrado['entregas_prazo'].sum() / (df_filtrado['entregas_prazo'].sum() + df_filtrado['entregas_atraso'].sum())) * 100 if (df_filtrado['entregas_prazo'].sum() + df_filtrado['entregas_atraso'].sum()) > 0 else 0
col1.metric("SLA de Entrega (%)", f"{sla:.1f}%")

# 2. QUALIDADE
qualidade = (df_filtrado['entregas_sem_problema'].sum() / (df_filtrado['entregas_sem_problema'].sum() + df_filtrado['entregas_com_problema'].sum())) * 100 if (df_filtrado['entregas_sem_problema'].sum() + df_filtrado['entregas_com_problema'].sum()) > 0 else 0
col2.metric("Qualidade da Entrega (%)", f"{qualidade:.1f}%")

# 3. CUSTO (Acima da Tabela)
custo_acima = df_filtrado['custo_acima_tabela'].sum()
col3.metric("Entregas Acima Tabela", f"{int(custo_acima)}")

# 4. META DE LITROS (Espaço para adição posterior)
meta_total = df_filtrado['meta_litros'].sum()
col4.metric("Meta de Litros (Total)", f"{meta_total:,.0f} L")

st.divider()

# --- GRÁFICOS ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Custo por Categoria")
    custos = {
        'Tabelado': df_filtrado['custo_tabelado'].sum(),
        'Acima Tabela': df_filtrado['custo_acima_tabela'].sum(),
        'Terceiros': df_filtrado['custo_terceiros'].sum()
    }
    fig_custo = px.pie(values=list(custos.values()), names=list(custos.keys()), 
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_custo, use_container_width=True)

with row1_col2:
    st.subheader("Evolução de Paletes e Carregamentos")
    fig_evolucao = go.Figure()
    fig_evolucao.add_trace(go.Scatter(x=df_filtrado['data_referencia'], y=df_filtrado['paletes'], name='Paletes', mode='lines+markers'))
    fig_evolucao.add_trace(go.Bar(x=df_filtrado['data_referencia'], y=df_filtrado['carregamentos_sudeste'] + df_filtrado['carregamentos_nordeste'], name='Total Carregamentos'))
    st.plotly_chart(fig_evolucao, use_container_width=True)

# Tabela de Dados Brutos
if st.checkbox("Ver Dados Brutos"):
    st.write(df_filtrado)

st.info("Para atualizar os dados, basta adicionar uma nova linha ao arquivo `dados_logistica.csv` no repositório.")
