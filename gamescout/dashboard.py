import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import sqlite3
import os

st.set_page_config(page_title="Dashboard", layout="wide", page_icon="📊")

DB_PATH = "data/processed/gamescout.db"

@st.cache_data(ttl=3600)
def load_data():
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            p.product_id AS ID_Producto,
            p.title AS Titulo,
            p.price_eur AS Precio_EUR,
            t.name AS Categoria,
            p.scraped_at AS Fecha_Extraccion
        FROM product p
        LEFT JOIN producttype t ON p.type_id = t.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['Fecha_Extraccion'] = pd.to_datetime(df['Fecha_Extraccion'])
    return df


st.title("📊 Dashboard EDA - GameScout")

with st.spinner("Cargando datos desde la base de datos..."):
    df = load_data()

if df is None:
    st.error(f"No se encontró la base de datos en: {DB_PATH}")
    st.stop()
elif df.empty:
    st.warning("La base de datos está vacía.")
    st.stop()
else:
    st.success("¡Datos cargados correctamente!")

with st.sidebar:
    st.header("⚙️ Configuración")
    st.write("Ajusta los parámetros del gráfico:")

    categorias = st.multiselect(
        "Filtrar por Categoría:",
        options=df['Categoria'].dropna().unique(),
        default=df['Categoria'].dropna().unique()
    )

    precio_max = st.slider(
        "Precio Máximo (€)",
        min_value=0.0,
        max_value=float(df['Precio_EUR'].max()),
        value=float(df['Precio_EUR'].max())
    )
if len(categorias) == 0:
    categorias = df['Categoria'].dropna().unique()

df_filtrado = df[(df['Categoria'].isin(categorias)) & (df['Precio_EUR'] <= precio_max)]

st.subheader("Estadísticas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Juegos", df_filtrado.shape[0])
col2.metric("Precio Promedio", f"€ {df_filtrado['Precio_EUR'].mean():.2f}")
col3.metric("Juego Más Caro", f"€ {df_filtrado['Precio_EUR'].max():.2f}")

st.divider()

tab1, tab2, tab3= st.tabs(["top 10", "Distribuciones", "Relaciones"])

with tab1:
    st.subheader("Top 10 mas caros")
    top10 = df_filtrado.sort_values(by="Precio_EUR", ascending=False).head(10)
    fig_top10 = px.bar(top10,x="Precio_EUR",y="Titulo",orientation="h", color="Categoria", barmode="group")
    fig_top10.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top10, use_container_width=True)
with tab2:
    st.subheader("Histograma de Precios")
    fig_hist = px.histogram(df_filtrado, x="Precio_EUR", color_discrete_sequence=['#3366CC'])
    st.plotly_chart(fig_hist, use_container_width=True)
with tab3:
    st.subheader("Promedio de Precios por Categoría")
    precio_promedio = df_filtrado.groupby("Categoria")["Precio_EUR"].mean().reset_index()
    fig_promedios = px.bar(
        precio_promedio,
        x="Categoria",
        y="Precio_EUR",
        color="Categoria",
        text_auto='.2f'
    )
    fig_promedios.update_layout(xaxis={'categoryorder': 'total descending'})
    st.plotly_chart(fig_promedios, use_container_width=True)
with st.expander("Ver más detalles de los datos y exportar"):
    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar CSV Filtrado",
        data=csv,
        file_name="gamescout_filtrado.csv",
        mime="text/csv"
    )