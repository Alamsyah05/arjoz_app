import streamlit as st
import sqlite3
import pandas as pd
from math import sqrt


# -----------------------------
# Ambil data bahan baku
# -----------------------------
def fetch_bahan_baku():
    con = sqlite3.connect("inventory.db")
    df = pd.read_sql_query("""
        SELECT id_bahan_baku, nama_bahan_baku, satuan_bahan_baku, lead_time, biaya_pesan, biaya_simpan
        FROM stok_bahan_baku
    """, con)
    con.close()
    return df


# -----------------------------
# Ambil stok bahan baku terkini
# -----------------------------
def fetch_stok():
    con = sqlite3.connect("inventory.db")

    masuk = pd.read_sql_query("""
        SELECT id_bahan_baku, SUM(jumlah_bahan_baku) as total_masuk
        FROM bahan_baku_masuk GROUP BY id_bahan_baku
    """, con)

    keluar = pd.read_sql_query("""
        SELECT id_bahan_baku, SUM(jumlah_bahan_baku) as total_keluar
        FROM bahan_baku_keluar GROUP BY id_bahan_baku
    """, con)

    con.close()

    stok = pd.merge(masuk, keluar, on="id_bahan_baku", how="left").fillna(0)
    stok["stok"] = stok["total_masuk"] - stok["total_keluar"]

    return dict(zip(stok["id_bahan_baku"], stok["stok"]))


# -----------------------------
# Session State
# -----------------------------
if "hasil" not in st.session_state:
    st.session_state.hasil = []

if "show_dialog" not in st.session_state:
    st.session_state.show_dialog = False


# -----------------------------
# Perhitungan EOQ, Safety Stock, ROP
# -----------------------------
def hitung(demand_harian, lead_time, S, H):
    D = demand_harian * 288  # asumsi 288 hari kerja / tahun
    EOQ = sqrt((2 * D * S) / H) if H > 0 else 0
    Safety_Stock = 0
    ROP = demand_harian * lead_time
    return round(EOQ, 2), round(Safety_Stock, 2), round(ROP, 2)


# -----------------------------
# Dialog Input
# -----------------------------
@st.dialog("Input Perhitungan")
def form_input():
    df = fetch_bahan_baku()

    if df.empty:
        st.warning("⚠️ Tidak ada data bahan baku di database!")
        return

    bahan_dict = {row["nama_bahan_baku"]: row for _, row in df.iterrows()}

    nama = st.selectbox("Pilih Bahan Baku", list(bahan_dict.keys()))
    demand_harian = st.number_input("Demand Harian", min_value=0.0, step=0.1)

    if st.button("💾 Hitung & Simpan"):
        row = bahan_dict[nama]
        EOQ, SS, ROP = hitung(
            demand_harian, row["lead_time"], row["biaya_pesan"], row["biaya_simpan"]
        )

        st.session_state.hasil.append([
            row["id_bahan_baku"],
            row["nama_bahan_baku"],
            demand_harian,
            EOQ,
            SS,
            ROP,
            row["satuan_bahan_baku"]
        ])

        st.success("✅ Perhitungan berhasil ditambahkan!")
        st.session_state.show_dialog = False
        st.rerun()


# -----------------------------
# UI
# -----------------------------
st.title("📦 Perhitungan EOQ, Safety Stock, dan ROP")

tab1, tab2 = st.tabs(["➕ Input Perhitungan", "📊 Hasil Perhitungan"])


# -----------------------------
# TAB 1
# -----------------------------
with tab1:
    st.subheader("Tambah Perhitungan Baru")

    if st.button("➕ Tambah Perhitungan"):
        st.session_state.show_dialog = True

    if st.session_state.show_dialog:
        form_input()


# -----------------------------
# TAB 2
# -----------------------------
with tab2:
    st.subheader("📊 Hasil Perhitungan")

    if len(st.session_state.hasil) == 0:
        st.info("Belum ada perhitungan dilakukan.")
    else:
        stok_dict = fetch_stok()

        header = st.columns([2.5, 1.3, 1.3, 1.3, 1.3, 1.3, 2.5, 1])
        header[0].markdown("**Nama Bahan Baku**")
        header[1].markdown("**EOQ**")
        header[2].markdown("**Safety Stock**")
        header[3].markdown("**ROP**")
        header[4].markdown("**Stok**")
        header[5].markdown("**Satuan**")
        header[6].markdown("**Rekomendasi**")
        header[7].markdown("**Aksi**")

        for i, row in enumerate(st.session_state.hasil):

            if len(row) == 6:  # auto fix format lama
                row = [None] + row
                st.session_state.hasil[i] = row

            id_bhn, nama, demand, eoq, ss, rop, satuan = row

            stok = stok_dict.get(id_bhn, 0)

            # Logika rekomendasi pembelian
            if stok <= rop:
                rekom = f"🔴 Pesan {eoq} {satuan} (Stok hampir habis)"
            elif stok <= ss:
                rekom = f"🟡 Waspada! Pertimbangkan pemesanan"
            else:
                rekom = f"🟢 Stok Aman"

            cols = st.columns([2.5, 1.3, 1.3, 1.3, 1.3, 1.3, 2.5, 1])

            cols[0].write(nama)
            cols[1].write(eoq)
            cols[2].write(ss)
            cols[3].write(rop)
            cols[4].write(stok)
            cols[5].write(satuan)
            cols[6].write(rekom)

            if cols[7].button("🗑️", key=f"hapus_{i}"):
                st.session_state.hasil.pop(i)
                st.rerun()
