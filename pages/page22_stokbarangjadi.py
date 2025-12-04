import streamlit as st
import pandas as pd
import sqlite3
from db_setup import init_db

# Inisialisasi DB
init_db()

# -----------------------------
# Fungsi Database
# -----------------------------


def fetch_all_records_with_stok():
    """Ambil semua barang jadi + stok terkini"""
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("""
        SELECT s.id_barang_jadi,
               s.nama_barang_jadi,
               s.grade_barang_jadi,
               s.satuan_barang_jadi,
               s.harga_barang_jadi,
               COALESCE(masuk.total_masuk, 0) AS total_masuk,
               COALESCE(keluar.total_keluar, 0) AS total_keluar,
               COALESCE(masuk.total_masuk, 0) - COALESCE(keluar.total_keluar, 0) AS stok
        FROM stok_barang_jadi s
        LEFT JOIN (
            SELECT id_barang_jadi, SUM(jumlah_barang_jadi) AS total_masuk
            FROM produk_jadi_masuk
            GROUP BY id_barang_jadi
        ) masuk ON s.id_barang_jadi = masuk.id_barang_jadi
        LEFT JOIN (
            SELECT id_barang_jadi, SUM(jumlah_barang_jadi) AS total_keluar
            FROM produk_jadi_keluar
            GROUP BY id_barang_jadi
        ) keluar ON s.id_barang_jadi = keluar.id_barang_jadi
        ORDER BY s.nama_barang_jadi ASC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def add_record(data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'INSERT INTO stok_barang_jadi (nama_barang_jadi, grade_barang_jadi, satuan_barang_jadi, harga_barang_jadi) VALUES (?, ?, ?, ?)',
        data
    )
    con.commit()
    con.close()


def update_record(id_barang_jadi, data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'UPDATE stok_barang_jadi SET nama_barang_jadi = ?, grade_barang_jadi = ?, satuan_barang_jadi = ?, harga_barang_jadi = ? WHERE id_barang_jadi = ?',
        (*data, id_barang_jadi)
    )
    con.commit()
    con.close()


def delete_record(id_barang_jadi):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM stok_barang_jadi WHERE id_barang_jadi = ?', (id_barang_jadi,))
    con.commit()
    con.close()


# -----------------------------
# Session State
# -----------------------------
if "show_add_dialog" not in st.session_state:
    st.session_state.show_add_dialog = False

if "dialog_type" not in st.session_state:
    st.session_state.dialog_type = None

if "active_record" not in st.session_state:
    st.session_state.active_record = None

# -----------------------------
# Streamlit App
# -----------------------------
st.title("📦 Stok Barang Jadi")
tab1, tab2 = st.tabs(["➕ Tambah Data", "📋 Lihat & Kelola Data"])

# -----------------------------
# Tab1: Tambah Data
# -----------------------------
with tab1:
    st.subheader("Tambah Barang Jadi Baru")

    if st.button('➕ Tambah Barang Jadi'):
        st.session_state.show_add_dialog = True

        @st.dialog("Form Tambah Barang Jadi")
        def tambah_dialog():
            nama_barang_jadi = st.text_input("Nama Barang Jadi")
            grade_barang_jadi = st.selectbox(
                "Grade Barang Jadi", ["B1", "B2", "B3", "B4", "B5", "B6"])
            satuan_barang_jadi = st.selectbox("Satuan Barang Jadi", ["Slop"])
            harga_barang_jadi = st.number_input(
                "Harga Barang Jadi", min_value=0, value=0)

            if st.button("💾 Simpan Data"):
                if not (nama_barang_jadi and grade_barang_jadi and satuan_barang_jadi):
                    st.warning("Semua kolom harus diisi!")
                else:
                    add_record(
                        (nama_barang_jadi, grade_barang_jadi,
                         satuan_barang_jadi, harga_barang_jadi)
                    )
                    st.success("✅ Data berhasil disimpan!")
                    st.session_state.show_add_dialog = False
                    st.rerun()

        if st.session_state.show_add_dialog:
            tambah_dialog()

# -----------------------------
# Tab2: Lihat & Kelola Data
# -----------------------------
with tab2:
    st.subheader("Daftar Stok Barang Jadi")
    data = fetch_all_records_with_stok()

    if not data:
        st.info("Belum ada data Barang Jadi.")
    else:
        # Header kolom
        header_cols = st.columns([2, 1, 1, 1, 1, 1])
        header_cols[0].markdown("**Nama Barang Jadi**")
        header_cols[1].markdown("**Grade**")
        header_cols[2].markdown("**Stok**")
        header_cols[3].markdown("**Satuan**")
        header_cols[4].markdown("**Harga**")
        header_cols[5].markdown("**Aksi**")

        # Baris data
        for record in data:
            id_barang_jadi, nama, grade, satuan, harga, total_masuk, total_keluar, stok = record
            cols = st.columns([2, 1, 1, 1, 1, 1])
            cols[0].write(nama)
            cols[1].write(grade)
            cols[2].write(stok)
            cols[3].write(satuan)
            cols[4].write(f"Rp {harga:,.0f}".replace(",", "."))

            # Tombol edit & hapus
            btn_edit, btn_delete = cols[5].columns([1, 1])
            with btn_edit:
                if st.button("✏️", key=f"edit_{id_barang_jadi}", help="Edit"):
                    st.session_state.dialog_type = "edit"
                    st.session_state.active_record = (
                        id_barang_jadi, nama, grade, satuan, harga)
            with btn_delete:
                if st.button("🗑️", key=f"delete_{id_barang_jadi}", help="Hapus"):
                    st.session_state.dialog_type = "delete"
                    st.session_state.active_record = (
                        id_barang_jadi, nama, grade, satuan, harga)

        # -----------------------------
        # Dialog Universal (Edit / Delete)
        # -----------------------------
        @st.dialog("Form Data Barang Jadi")
        def universal_dialog(record, mode):
            id_barang_jadi, nama, grade, satuan, harga = record

            if mode == "edit":
                st.subheader("✏️ Edit Data Barang Jadi")
                new_nama = st.text_input("Nama Barang Jadi", value=nama)
                new_grade = st.selectbox("Grade Barang Jadi", ["B1", "B2", "B3", "B4", "B5", "B6"],
                                         index=["B1", "B2", "B3", "B4", "B5", "B6"].index(grade))
                new_satuan = st.selectbox("Satuan Barang Jadi", ["Slop"],
                                          index=["Slop"].index(satuan))
                new_harga = st.number_input(
                    "Harga Barang Jadi", min_value=0, value=harga)

                if st.button("💾 Simpan Perubahan"):
                    update_record(id_barang_jadi, (new_nama,
                                  new_grade, new_satuan, new_harga))
                    st.success("✅ Data berhasil diperbarui!")
                    st.session_state.dialog_type = None
                    st.session_state.active_record = None
                    st.rerun()

            elif mode == "delete":
                st.subheader("⚠️ Konfirmasi Penghapusan")
                st.warning(
                    f"Apakah Anda yakin ingin menghapus **{nama} ({grade}, {satuan})**?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Batal"):
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()
                with col2:
                    if st.button("✅ Hapus"):
                        delete_record(id_barang_jadi)
                        st.success("✅ Data berhasil dihapus!")
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()

        if st.session_state.dialog_type and st.session_state.active_record:
            universal_dialog(st.session_state.active_record,
                             st.session_state.dialog_type)
