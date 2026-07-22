import streamlit as st
import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import sqlite3
import os
import numpy as np
from app.stats import category_stats  # type: ignore[import-not-found]

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
            p.type_id AS Categoria_ID, -- AQUÍ ESTÁ EL ID
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
    st.header("⚙Configuración")
    st.write("Ajusta los parámetros del gráfico:")
    buscador = st.text_input("buscar juego")

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
if buscador:
    df_filtrado = df_filtrado[df['Titulo'].str.contains(buscador, case=False, na=False)]
st.subheader("Estadísticas Generales")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Juegos", df_filtrado.shape[0])
col2.metric("Precio Promedio", f"€ {df_filtrado['Precio_EUR'].mean():.2f}")
col3.metric("Juego Más Caro", f"€ {df_filtrado['Precio_EUR'].max():.2f}")

st.divider()

tab1, tab2, tab3, tab4= st.tabs(["top 10", "Distribuciones", "Relaciones", "Resumen por categoria"])

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
with tab4:
    st.subheader("Resumen Estadístico por Categoría (Motor Numba)")
    preciostab4 = df_filtrado['Precio_EUR'].to_numpy(dtype=np.float32)
    categoriastab4 = df_filtrado['Categoria'].to_numpy()
    categoriastab4 = df_filtrado['Categoria'].dropna().unique()
    resultadostab4 = []
    for cat in categoriastab4:
        idtab4 = np.where(categoriastab4 == cat)[0]
        c_max, c_min, c_mean, c_std = category_stats(preciostab4, idtab4)
        resultadostab4.append({
            "Categoria": cat,
            "Mínimo": c_min,
            "Promedio": c_mean,
            "Máximo": c_max,
            "Desviación Estándar": c_std
        })
    if resultadostab4:
        df_resumen = pd.DataFrame(resultadostab4)
        st.dataframe(
            df_resumen.style.format({
                "Mínimo": "{:.2f}",
                "Promedio": "{:.2f}",
                "Máximo": "{:.2f}",
                "Desviación Estándar": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
        fig_resumen = px.bar(
            df_resumen,
            x="Categoria",
            y=["Mínimo", "Promedio", "Máximo"],
            barmode="group",
            text_auto=".2f",
            title="Comparativa de Precios por Categoría",
            labels={"value": "Precio (€)", "variable": "Métrica"}
        )
        fig_resumen.update_layout(yaxis_title="Euros (€)")
        st.plotly_chart(fig_resumen, use_container_width=True)
with st.expander("Ver más detalles de los datos y exportar"):
    st.dataframe(df_filtrado, use_container_width=True)

    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar CSV Filtrado",
        data=csv,
        file_name="gamescout_filtrado.csv",
        mime="text/csv"
    )