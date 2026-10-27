import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="GDELT Real-Time Event Dashboard", layout="wide", page_icon="🌐")

# Konfigurasi path database yang fleksibel untuk pengembangan lokal (Windows) dan Docker bind mount
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdelt.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database DuckDB tidak ditemukan pada path: {DB_PATH}")

    con = duckdb.connect(DB_PATH, read_only=True)

    df = con.execute(
        "SELECT * FROM gdelt_events"
    ).df()

    logs_df = con.execute("""
        SELECT *
        FROM pipeline_logs
        ORDER BY execution_time DESC
        LIMIT 5
    """).df()

    con.close()

    return df, logs_df

st.title("🌐 GDELT Global Real-Time Event Analytics & Pipeline Monitor")
st.caption("Arsitektur Data Skala Besar Berbasis DuckDB, Streamlit, dan Speed Layer Ingestion")

try:
    df, logs_df = load_data()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events (DB)", f"{len(df):,}")
    with col2:
        today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
        today_events = len(df[df["EventDate"] == today_str]) if "EventDate" in df.columns else 0
        st.metric("Events Hari Ini", f"{today_events:,}")
    with col3:
        latest_latency = (
          logs_df["data_latency_minutes"].iloc[0]
          if not logs_df.empty else None
      )
    if pd.isna(latest_latency):
        st.metric("Data Latency", "Belum tersedia")
    else:
        st.metric("Data Latency", f"{latest_latency:.1f} Menit")
    with col4:
        last_status = logs_df["status"].iloc[0] if not logs_df.empty else "UNKNOWN"
        st.metric("Status Pipeline", last_status)
        
    st.divider()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Distribusi Kategori Peristiwa (QuadClass)")
        if "EventCategory" in df.columns and not df.empty:
            cat_df = df["EventCategory"].value_counts().reset_index()
            cat_df.columns = ["EventCategory", "Count"]
            fig_pie = px.pie(cat_df, names="EventCategory", values="Count", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie, width="stretch")
        else:
            st.info("Data kategori belum tersedia.")
        
    with col_right:
        st.subheader("🌍 Top 10 Negara Aktor Utamanya (Actor1)")
        if "Actor1CountryCode" in df.columns and not df.empty:
            top_country = df["Actor1CountryCode"].value_counts().dropna().head(10).reset_index()
            top_country.columns = ["Country", "Count"]
            fig_bar = px.bar(top_country, x="Count", y="Country", orientation="h",
                             color="Count", color_continuous_scale="Viridis")
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, width="stretch")
        else:
            st.info("Data negara aktor belum tersedia.")
        
    st.subheader("📍 Peta Sebaran Lokasi Peristiwa Global")
    if "ActionGeo_Lat" in df.columns and "ActionGeo_Long" in df.columns:
        map_df = df.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"]).copy()
        if not map_df.empty:
            fig_map = px.scatter_geo(
                map_df.head(2000),
                lat="ActionGeo_Lat",
                lon="ActionGeo_Long",
                hover_name="ActionGeo_FullName" if "ActionGeo_FullName" in map_df.columns else None,
                color="EventCategory" if "EventCategory" in map_df.columns else None,
                size_max=10,
                projection="natural earth",
                title="Sampel 2.000 Lokasi Kejadian Terakhir"
            )
            st.plotly_chart(fig_map, width="stretch")
        else:
            st.info("Koordinat lokasi peristiwa belum tersedia.")
        
    st.subheader("🔍 Pencarian Peristiwa & Sumber Berita Interaktif")
    search_keyword = st.text_input("Cari kata kunci Nama Aktor atau URL Berita:", "")
    
    if search_keyword:
        filtered_df = df[
            (df["Actor1Name"].astype(str).str.contains(search_keyword, case=False, na=False)) |
            (df["SOURCEURL"].astype(str).str.contains(search_keyword, case=False, na=False))
        ]
    else:
        filtered_df = df
        
    display_cols = [col for col in ["GLOBALEVENTID", "SQLDATE", "EventCategory", "Actor1Name", "Actor2Name", "SOURCEURL"] if col in df.columns]
    st.dataframe(filtered_df[display_cols].head(100), width="stretch")

except Exception as e:
    st.error(f"Gagal memuat dasbor: {e}")
