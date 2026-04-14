import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="Gestao de Logistica e Fretes", layout="wide")

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'Relatorio de Logistica e Fretes', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, f'Data de Geracao: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        self.ln(10)

def generate_pdf(df_filtrado, total_frete, sla, qualidade):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Resumo de Performance', 0, 1, 'L', fill=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(60, 10, f"Valor Total Frete: R$ {total_frete:,.2f}", 1)
    pdf.cell(60, 10, f"SLA Entrega: {sla:.1f}%", 1)
    pdf.cell(60, 10, f"Qualidade: {qualidade:.1f}%", 1)
    pdf.ln(15)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(40, 10, 'Carregamento', 1)
    pdf.cell(40, 10, 'Entrega', 1)
    pdf.cell(60, 10, 'Distribuidor', 1)
    pdf.cell(50, 10, 'Valor Viagem', 1)
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 8)
    for _, row in df_filtrado.iterrows():
        pdf.cell(40, 10, str(row['data_carregamento'].date()), 1)
        pdf.cell(40, 10, str(row['data_entrega'].date()), 1)
        pdf.cell(60, 10, str(row['distribuidor']), 1)
        pdf.cell(50, 10, f"R$ {row['valor_frete_total']:,.2f}", 1)
        pdf.ln()
    return bytes(pdf.output())

@st.cache_data
def load_data():
    df = pd.read_csv('dados_logistica.csv')
    df['data_carregamento'] = pd.to_datetime(df['data_carregamento'])
    df['data_entrega'] = pd.to_datetime(df['data_entrega'])
    return df

df = load_data()

st.title("Gestao de Fretes e Performance de Entrega")

st.sidebar.header("Filtros")
distribuidores = st.sidebar.multiselect("Selecionar Distribuidoras:", df['distribuidor'].unique(), default=df['distribuidor'].unique())
df_filtrado = df[df['distribuidor'].isin(distribuidores)]

total_frete = df_filtrado.drop_duplicates('id_viagem')['valor_frete_total'].sum()
total_paletes = df_filtrado['paletes'].sum()
total_entregas = df_filtrado['entregas_prazo'].sum() + df_filtrado['entregas_atraso'].sum()
sla = (df_filtrado['entregas_prazo'].sum() / total_entregas * 100) if total_entregas > 0 else 0
total_qualidade = df_filtrado['entregas_sem_problema'].sum() + df_filtrado['entregas_com_problema'].sum()
qualidade = (df_filtrado['entregas_sem_problema'].sum() / total_qualidade * 100) if total_qualidade > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Valor Total Frete", f"R$ {total_frete:,.2f}")
c2.metric("SLA de Entrega", f"{sla:.1f}%")
c3.metric("Qualidade de Entrega", f"{qualidade:.1f}%")
c4.metric("Volume de Paletes", f"{int(total_paletes)}")

st.divider()

g1, g2 = st.columns(2)
with g1:
    st.subheader("Custos por ID de Viagem")
    df_viagem = df_filtrado.drop_duplicates('id_viagem')
    fig_v = px.bar(df_viagem, x='id_viagem', y='valor_frete_total', color='id_viagem', title="Comparativo Financeiro")
    st.plotly_chart(fig_v, use_container_width=True)

with g2:
    st.subheader("Tempo Medio entre Carregamento e Entrega")
    df_filtrado['dias_transporte'] = (df_filtrado['data_entrega'] - df_filtrado['data_carregamento']).dt.days
    fig_t = px.box(df_filtrado, x='distribuidor', y='dias_transporte', title="Lead Time por Distribuidor")
    st.plotly_chart(fig_t, use_container_width=True)

st.sidebar.divider()
st.sidebar.subheader("Exportar Relatorios")
csv_data = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download CSV", csv_data, "dados_logistica.csv", "text/csv")

if st.sidebar.button("Gerar Relatorio PDF"):
    pdf_bytes = generate_pdf(df_filtrado, total_frete, sla, qualidade)
    st.sidebar.download_button("Confirmar Download PDF", pdf_bytes, "relatorio_logistica.pdf", "application/pdf")

st.subheader("Detalhamento de Entregas e Datas")
st.dataframe(df_filtrado[['data_carregamento', 'data_entrega', 'distribuidor', 'paletes', 'valor_frete_total', 'id_viagem']], use_container_width=True)
