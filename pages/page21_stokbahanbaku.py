import streamlit as st
import pandas as pd
import sqlite3
from db_setup import init_db

# Inisialisasi DB
init_db()

# -----------------------------
# Fungsi Database
# -----------------------------


def fetch_all_records():
    """Ambil semua bahan baku + stok terkini + parameter EOQ"""
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("""
        SELECT s.id_bahan_baku,
               s.nama_bahan_baku,
               s.satuan_bahan_baku,
               s.lead_time,
               s.biaya_pesan,
               s.biaya_simpan,
               COALESCE(masuk.total_masuk, 0) AS total_masuk,
               COALESCE(keluar.total_keluar, 0) AS total_keluar,
               COALESCE(masuk.total_masuk, 0) - COALESCE(keluar.total_keluar, 0) AS stok
        FROM stok_bahan_baku s
        LEFT JOIN (
            SELECT id_bahan_baku, SUM(jumlah_bahan_baku) AS total_masuk
            FROM bahan_baku_masuk
            GROUP BY id_bahan_baku
        ) masuk ON s.id_bahan_baku = masuk.id_bahan_baku
        LEFT JOIN (
            SELECT id_bahan_baku, SUM(jumlah_bahan_baku) AS total_keluar
            FROM bahan_baku_keluar
            GROUP BY id_bahan_baku
        ) keluar ON s.id_bahan_baku = keluar.id_bahan_baku
        ORDER BY s.id_bahan_baku ASC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def add_record(data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'INSERT INTO stok_bahan_baku (nama_bahan_baku, satuan_bahan_baku, lead_time, biaya_pesan, biaya_simpan) VALUES (?, ?, ?, ?, ?)',
        data
    )
    con.commit()
    con.close()


def update_record(id_bahan_baku, data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'UPDATE stok_bahan_baku SET nama_bahan_baku = ?, satuan_bahan_baku = ?, lead_time = ?, biaya_pesan = ?, biaya_simpan = ? WHERE id_bahan_baku = ?',
        (*data, id_bahan_baku)
    )
    con.commit()
    con.close()


def delete_record(id_bahan_baku):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM stok_bahan_baku WHERE id_bahan_baku = ?', (id_bahan_baku,))
    con.commit()
    con.close()


# -----------------------------
# Session State
# -----------------------------
if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = False

if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None


# -----------------------------
# Streamlit App
# -----------------------------
st.title("📦 Stok Bahan Baku")
tab1, tab2 = st.tabs(["➕ Tambah Data", "📋 Lihat & Kelola Data"])

# -----------------------------
# Tab1: Tambah Data
# -----------------------------
with tab1:
    st.subheader("Tambah Bahan Baku Baru")

    if st.button('➕ Tambah Bahan Baku'):
        st.session_state.show_add_dialog = True

        @st.dialog("Form Tambah Bahan Baku")
        def tambah_dialog():
            nama_bahan_baku = st.text_input("Nama Bahan Baku")
            satuan_bahan_baku = st.selectbox(
                "Satuan Bahan Baku", ["Kg", "Kaleng", "Lembar", "Gulungan", "Unit", "Dus", "Lusin"])
            lead_time = st.number_input(
                "Lead Time (hari)", min_value=0, value=0)
            biaya_pesan = st.number_input(
                "Biaya Pesan (Rp)", min_value=0, value=0)
            biaya_simpan = st.number_input(
                "Biaya Simpan (Rp/unit/period)", min_value=0, value=0)

            if st.button("💾 Simpan Data"):
                if not nama_bahan_baku:
                    st.warning("Nama Bahan Baku wajib diisi!")
                else:
                    add_record((nama_bahan_baku, satuan_bahan_baku,
                               lead_time, biaya_pesan, biaya_simpan))
                    st.success("✅ Data berhasil disimpan!")
                    st.session_state.show_add_dialog = False
                    st.rerun()

        if st.session_state.show_add_dialog:
            tambah_dialog()
# -----------------------------
# Tab2: Lihat & Kelola Data
# -----------------------------
with tab2:
    st.subheader("Daftar Stok Bahan Baku")
    data = fetch_all_records()

    if not data:
        st.info("Belum ada data bahan baku.")
    else:
        # Header kolom
        header_cols = st.columns([2, 1, 1, 1, 1, 1, 1])
        header_cols[0].markdown("**Nama Bahan Baku**")
        header_cols[1].markdown("**Stok**")
        header_cols[2].markdown("**Satuan**")
        header_cols[3].markdown("**Lead Time (hari)**")
        header_cols[4].markdown("**Biaya Pesan**")
        header_cols[5].markdown("**Biaya Simpan**")
        header_cols[6].markdown("**Aksi**")

        if "dialog_type" not in st.session_state:
            st.session_state.dialog_type = None
        if "active_record" not in st.session_state:
            st.session_state.active_record = None

        for record in data:
            id_bahan_baku, nama, satuan, lead, pesan, simpan, total_masuk, total_keluar, stok = record
            cols = st.columns([2, 1, 1, 1, 1, 1, 1])

            cols[0].write(nama)
            cols[1].write(stok)
            cols[2].write(satuan)
            cols[3].write(lead)
            cols[4].write(f"Rp {pesan:,.0f}".replace(",", "."))
            cols[5].write(f"Rp {simpan:,.0f}".replace(",", "."))

            btn_edit, btn_delete = cols[6].columns([1, 1])
            with btn_edit:
                if st.button("✏️", key=f"edit_{id_bahan_baku}", help="Edit"):
                    st.session_state.dialog_type = "edit"
                    st.session_state.active_record = (
                        id_bahan_baku, nama, satuan, lead, pesan, simpan)
            with btn_delete:
                if st.button("🗑️", key=f"delete_{id_bahan_baku}", help="Hapus"):
                    st.session_state.dialog_type = "delete"
                    st.session_state.active_record = (
                        id_bahan_baku, nama, satuan, lead, pesan, simpan)

        @st.dialog("Form Data Bahan Baku")
        def universal_dialog(record, mode):
            id_bahan_baku, nama, satuan, lead, pesan, simpan = record

            if mode == "edit":
                st.subheader("✏️ Edit Data")
                new_nama = st.text_input("Nama Bahan Baku", value=nama)
                new_satuan = st.selectbox("Satuan", ["Kg", "Kaleng", "Lembar", "Gulungan", "Unit", "Dus", "Lusin"], index=[
                                          "Kg", "Kaleng", "Lembar", "Gulungan", "Unit", "Dus", "Lusin"].index(satuan))
                new_lead = st.number_input(
                    "Lead Time (hari)", min_value=0, value=lead)
                new_pesan = st.number_input(
                    "Biaya Pesan (Rp)", min_value=0.0, value=pesan)
                new_simpan = st.number_input(
                    "Biaya Simpan (Rp)", min_value=0.0, value=simpan)

                if st.button("💾 Simpan Perubahan"):
                    update_record(id_bahan_baku, (new_nama,
                                  new_satuan, new_lead, new_pesan, new_simpan))
                    st.success("✅ Data berhasil diperbarui!")
                    st.session_state.dialog_type = None
                    st.session_state.active_record = None
                    st.rerun()

            elif mode == "delete":
                st.subheader("⚠️ Konfirmasi Penghapusan")
                st.warning(
                    f"Apakah Anda yakin ingin menghapus **{nama} ({satuan})**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Batal"):
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()
                with col2:
                    if st.button("✅ Hapus"):
                        delete_record(id_bahan_baku)
                        st.success("✅ Data berhasil dihapus!")
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()

        if st.session_state.dialog_type and st.session_state.active_record:
            universal_dialog(st.session_state.active_record,
                             st.session_state.dialog_type)
