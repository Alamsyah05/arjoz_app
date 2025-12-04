import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# st.set_page_config(page_title="Dashboard Inventory", layout="wide")

# -----------------------------
# Custom CSS untuk card dengan gradasi hijau kehitaman
# -----------------------------
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a4d2e 0%, #2d6a4f 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: bold;
        color: white !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 15px;
        font-weight: 500;
        color: #d4edda !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #a8dadc !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Fungsi ambil data
# -----------------------------


def get_data(query):
    con = sqlite3.connect("inventory.db")
    df = pd.read_sql_query(query, con)
    con.close()
    return df

# -----------------------------
# Hitung stok bahan baku
# -----------------------------


def get_stok_bahan_baku():
    masuk = get_data("""
        SELECT id_bahan_baku, SUM(jumlah_bahan_baku) as total_masuk
        FROM bahan_baku_masuk GROUP BY id_bahan_baku
    """)
    keluar = get_data("""
        SELECT id_bahan_baku, SUM(jumlah_bahan_baku) as total_keluar
        FROM bahan_baku_keluar GROUP BY id_bahan_baku
    """)
    stok = pd.merge(masuk, keluar, on="id_bahan_baku", how="left").fillna(0)
    stok["stok"] = stok["total_masuk"] - stok["total_keluar"]

    bahan_baku = get_data("SELECT * FROM stok_bahan_baku")
    result = pd.merge(bahan_baku, stok[[
                      "id_bahan_baku", "stok"]], on="id_bahan_baku", how="left").fillna(0)
    return result

# -----------------------------
# Hitung stok barang jadi
# -----------------------------


def get_stok_barang_jadi():
    masuk = get_data("""
        SELECT id_barang_jadi, SUM(jumlah_barang_jadi) as total_masuk
        FROM produk_jadi_masuk GROUP BY id_barang_jadi
    """)
    keluar = get_data("""
        SELECT id_barang_jadi, SUM(jumlah_barang_jadi) as total_keluar
        FROM produk_jadi_keluar GROUP BY id_barang_jadi
    """)
    stok = pd.merge(masuk, keluar, on="id_barang_jadi", how="left").fillna(0)
    stok["stok"] = stok["total_masuk"] - stok["total_keluar"]

    barang_jadi = get_data("SELECT * FROM stok_barang_jadi")
    result = pd.merge(barang_jadi, stok[[
                      "id_barang_jadi", "stok"]], on="id_barang_jadi", how="left").fillna(0)
    return result


# =============================
# DASHBOARD
# =============================

st.title("📊 Dashboard Inventory")

bahan_baku_df = get_stok_bahan_baku()
barang_jadi_df = get_stok_barang_jadi()

# Summary cards dengan HTML Custom
col1, col2, col3, col4 = st.columns(4)

# background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);; 
                padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
        <p style='color: #a8dadc; font-size: 14px; margin: 0;'>Total Jenis Bahan Baku</p>
        <h2 style='color: white; font-size: 36px; margin: 10px 0 0 0;'>{len(bahan_baku_df)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);; 
                padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
        <p style='color: #a8dadc; font-size: 14px; margin: 0;'>Total Jenis Barang Jadi</p>
        <h2 style='color: white; font-size: 36px; margin: 10px 0 0 0;'>{len(barang_jadi_df)}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);; 
                padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
        <p style='color: #d4edda; font-size: 14px; margin: 0;'>Total Stok Bahan Baku</p>
        <h2 style='color: white; font-size: 36px; margin: 10px 0 0 0;'>{bahan_baku_df['stok'].sum():,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: linear-gradient(180deg, #54744B 0%, #9EDA8D 100%);; 
                padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>
        <p style='color: #d4edda; font-size: 14px; margin: 0;'>Total Stok Barang Jadi</p>
        <h2 style='color: white; font-size: 36px; margin: 10px 0 0 0;'>{barang_jadi_df['stok'].sum():,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# Grafik Stok Bahan Baku
# -----------------------------
st.subheader("📦 Stok Bahan Baku")
fig_baku = px.bar(
    bahan_baku_df,
    x="nama_bahan_baku",
    y="stok",
    text="satuan_bahan_baku",
    color="stok",
    color_continuous_scale="greens",
    title="Stok Bahan Baku per Jenis"
)
fig_baku.update_layout(xaxis_title="Nama Bahan Baku",
                       yaxis_title="Jumlah Stok", hovermode="x unified")
st.plotly_chart(fig_baku, use_container_width=True)

print(bahan_baku_df)
# -----------------------------
# Grafik Stok Barang Jadi
# -----------------------------
st.subheader("🏭 Stok Barang Jadi")
barang_jadi_df["nama_barang"] = barang_jadi_df["nama_barang_jadi"] + \
    " (" + barang_jadi_df["grade_barang_jadi"] + ")"

fig_jadi = px.bar(
    barang_jadi_df,
    x="nama_barang",
    y="stok",
    text="satuan_barang_jadi",
    color="stok",
    color_continuous_scale="greens",
    title="Stok Barang Jadi per Produk"
)
fig_jadi.update_layout(xaxis_title="Nama Barang Jadi",
                       yaxis_title="Jumlah Stok", hovermode="x unified")
st.plotly_chart(fig_jadi, use_container_width=True)
