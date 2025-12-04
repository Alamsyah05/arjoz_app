import streamlit as st
import pandas as pd
import sqlite3
from db_setup import init_db

# Inisialisasi DB
init_db()

# -----------------------------
# Fungsi Database
# -----------------------------


def fetch_produk_jadi():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("""
        SELECT id_barang_jadi, nama_barang_jadi, grade_barang_jadi, satuan_barang_jadi
        FROM stok_barang_jadi
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def fetch_all_records():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("""
        SELECT pjk.id_keluar, sbj.nama_barang_jadi, sbj.grade_barang_jadi, sbj.satuan_barang_jadi,
               pjk.tanggal, pjk.jumlah_barang_jadi
        FROM produk_jadi_keluar pjk
        JOIN stok_barang_jadi sbj ON pjk.id_barang_jadi = sbj.id_barang_jadi
        ORDER BY pjk.tanggal DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def add_record(data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'INSERT INTO produk_jadi_keluar (id_barang_jadi, tanggal, jumlah_barang_jadi) VALUES (?, ?, ?)',
        data
    )
    con.commit()
    con.close()


def update_record(id_keluar, data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'UPDATE produk_jadi_keluar SET id_barang_jadi = ?, tanggal = ?, jumlah_barang_jadi = ? WHERE id_keluar = ?',
        (*data, id_keluar)
    )
    con.commit()
    con.close()


def delete_record(id_keluar):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM produk_jadi_keluar WHERE id_keluar = ?', (id_keluar,))
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
st.title("📤 Produk Jadi Keluar")
tab1, tab2 = st.tabs(["➕ Tambah Data", "📋 Lihat & Kelola Data"])

# -----------------------------
# Tab1: Tambah Data
# -----------------------------
with tab1:
    st.subheader("Tambah Data Produk Jadi Keluar")

    if st.button('➕ Tambah Data Keluar'):
        st.session_state.show_add_dialog = True

        @st.dialog("Form Tambah Produk Jadi Keluar")
        def tambah_dialog():
            produk_list = fetch_produk_jadi()
            if not produk_list:
                st.warning(
                    "⚠️ Belum ada data produk jadi di tabel stok_barang_jadi!")
                return

            produk_dict = {
                f"{nama} - {grade} ({satuan})": id_produk
                for id_produk, nama, grade, satuan in produk_list
            }

            nama_produk = st.selectbox(
                "Pilih Produk Jadi", list(produk_dict.keys()))
            tanggal = st.date_input("Tanggal Keluar")
            jumlah = st.number_input(
                "Jumlah Produk Jadi", min_value=0, step=1)

            if st.button("💾 Simpan Data"):
                if not nama_produk or jumlah <= 0:
                    st.warning("Semua kolom harus diisi dengan benar!")
                else:
                    id_produk = produk_dict[nama_produk]
                    add_record((id_produk, str(tanggal), jumlah))
                    st.success("✅ Data berhasil disimpan!")
                    st.session_state.show_add_dialog = False
                    st.rerun()

        if st.session_state.show_add_dialog:
            tambah_dialog()

# -----------------------------
# Tab2: Lihat & Kelola Data
# -----------------------------
with tab2:
    st.subheader("Daftar Produk Jadi Keluar")
    data = fetch_all_records()

    if not data:
        st.info("Belum ada data produk jadi keluar.")
    else:
        # Header kolom
        header_cols = st.columns([1, 2, 1, 1, 1, 1])
        header_cols[0].markdown("**Tanggal Keluar**")
        header_cols[1].markdown("**Nama Produk Jadi**")
        header_cols[2].markdown("**Grade**")
        header_cols[3].markdown("**Jumlah**")
        header_cols[4].markdown("**Satuan**")
        header_cols[5].markdown("**Aksi**")

        # Session state tambahan
        if "dialog_type" not in st.session_state:
            st.session_state.dialog_type = None
        if "active_record" not in st.session_state:
            st.session_state.active_record = None

        # Baris data
        for record in data:
            id_keluar, nama, grade, satuan, tanggal, jumlah = record
            cols = st.columns([1, 2, 1, 1, 1, 1])
            cols[0].write(tanggal)
            cols[1].write(nama)
            cols[2].write(grade)
            cols[3].write(jumlah)
            cols[4].write(satuan)

            btn_edit, btn_delete = cols[5].columns([1, 1])
            with btn_edit:
                if st.button("✏️", key=f"edit_{id_keluar}", help="Edit"):
                    st.session_state.dialog_type = "edit"
                    st.session_state.active_record = record
            with btn_delete:
                if st.button("🗑️", key=f"delete_{id_keluar}", help="Hapus"):
                    st.session_state.dialog_type = "delete"
                    st.session_state.active_record = record

        # -----------------------------
        # Dialog Tunggal (Edit / Delete)
        # -----------------------------
        @st.dialog("Form Data Produk Jadi Keluar")
        def universal_dialog(record, mode):
            id_keluar, nama, grade, satuan, tanggal, jumlah = record

            if mode == "edit":
                st.subheader("✏️ Edit Data")
                produk_list = fetch_produk_jadi()
                produk_dict = {
                    f"{n} - {g} ({s})": i for i, n, g, s in produk_list}
                current_option = f"{nama} - {grade} ({satuan})"

                new_produk = st.selectbox(
                    "Pilih Produk Jadi",
                    list(produk_dict.keys()),
                    index=list(produk_dict.keys()).index(current_option)
                )
                new_tanggal = st.date_input(
                    "Tanggal Keluar", pd.to_datetime(tanggal))
                new_jumlah = st.number_input(
                    "Jumlah Produk Jadi", min_value=0.0, step=0.1, value=float(jumlah))

                if st.button("💾 Simpan Perubahan"):
                    update_record(
                        id_keluar, (produk_dict[new_produk], str(new_tanggal), new_jumlah))
                    st.success("✅ Data berhasil diperbarui!")
                    st.session_state.dialog_type = None
                    st.session_state.active_record = None
                    st.rerun()

            elif mode == "delete":
                st.subheader("⚠️ Konfirmasi Penghapusan")
                st.warning(
                    f"Apakah Anda yakin ingin menghapus data **{nama} ({jumlah} {satuan})** pada tanggal **{tanggal}**?"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Batal"):
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()
                with col2:
                    if st.button("✅ Hapus"):
                        delete_record(id_keluar)
                        st.success("✅ Data berhasil dihapus!")
                        st.session_state.dialog_type = None
                        st.session_state.active_record = None
                        st.rerun()

        # Jalankan dialog hanya jika ada yang aktif
        if st.session_state.dialog_type and st.session_state.active_record:
            universal_dialog(st.session_state.active_record,
                             st.session_state.dialog_type)