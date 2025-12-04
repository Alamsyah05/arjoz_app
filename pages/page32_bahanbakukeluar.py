import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from db_setup import init_db

# Inisialisasi DB
init_db()

# -----------------------------
# Fungsi Database
# -----------------------------


def fetch_bahan_baku():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        "SELECT id_bahan_baku, nama_bahan_baku, satuan_bahan_baku FROM stok_bahan_baku")
    rows = cur.fetchall()
    con.close()
    return rows


def fetch_all_records():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute("""
        SELECT bbk.id_keluar, sbb.nama_bahan_baku, sbb.satuan_bahan_baku, bbk.tanggal, bbk.jumlah_bahan_baku, bbk.id_bahan_baku
        FROM bahan_baku_keluar bbk
        JOIN stok_bahan_baku sbb ON bbk.id_bahan_baku = sbb.id_bahan_baku
        ORDER BY bbk.tanggal DESC
    """)
    rows = cur.fetchall()
    con.close()
    return rows


def add_record(data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'INSERT INTO bahan_baku_keluar (id_bahan_baku, tanggal, jumlah_bahan_baku) VALUES (?, ?, ?)',
        data
    )
    con.commit()
    con.close()


def update_record(id_keluar, data):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'UPDATE bahan_baku_keluar SET id_bahan_baku = ?, tanggal = ?, jumlah_bahan_baku = ? WHERE id_keluar = ?',
        (*data, id_keluar)
    )
    con.commit()
    con.close()


def delete_record(id_keluar):
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()
    cur.execute(
        'DELETE FROM bahan_baku_keluar WHERE id_keluar = ?', (id_keluar,))
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
st.title("📤 Bahan Baku Keluar")
tab1, tab2 = st.tabs(["➕ Tambah Data", "📋 Lihat & Kelola Data"])

# -----------------------------
# Tab1: Tambah Data
# -----------------------------
with tab1:
    st.subheader("Tambah Data Bahan Baku Keluar")

    if st.button('➕ Tambah Data Keluar'):
        st.session_state.show_add_dialog = True

        @st.dialog("Form Tambah Bahan Baku Keluar")
        def tambah_dialog():
            bahan_list = fetch_bahan_baku()
            if not bahan_list:
                st.warning(
                    "⚠️ Belum ada data bahan baku di tabel stok_bahan_baku!")
                return

            bahan_dict = {
                f"{nama} ({satuan})": id_bahan for id_bahan, nama, satuan in bahan_list}
            nama_bahan = st.selectbox(
                "Pilih Bahan Baku", list(bahan_dict.keys()))
            tanggal = st.date_input("Tanggal Keluar")
            jumlah = st.number_input(
                "Jumlah Bahan Baku", min_value=0.0, step=0.1)

            if st.button("💾 Simpan Data"):
                if not nama_bahan or jumlah <= 0:
                    st.warning("Semua kolom harus diisi dengan benar!")
                else:
                    id_bahan = bahan_dict[nama_bahan]
                    add_record((id_bahan, str(tanggal), jumlah))
                    st.success("✅ Data berhasil disimpan!")
                    st.session_state.show_add_dialog = False
                    st.rerun()

        if st.session_state.show_add_dialog:
            tambah_dialog()

# -----------------------------
# Tab2: Lihat & Kelola Data
# -----------------------------
with tab2:
    st.subheader("Daftar Bahan Baku Keluar")
    data = fetch_all_records()

    if not data:
        st.info("Belum ada data bahan baku keluar.")
    else:
        # Header kolom
        header_cols = st.columns([1, 2, 1, 1, 1])
        header_cols[0].markdown("**Tanggal Keluar**")
        header_cols[1].markdown("**Nama Bahan Baku**")
        header_cols[2].markdown("**Jumlah**")
        header_cols[3].markdown("**Satuan**")
        header_cols[4].markdown("**Aksi**")

        # Session state tambahan
        if "dialog_type" not in st.session_state:
            st.session_state.dialog_type = None
        if "active_record" not in st.session_state:
            st.session_state.active_record = None

        # Baris data
        for record in data:
            id_keluar, nama, satuan, tanggal, jumlah, id_bahan_baku = record
            cols = st.columns([1, 2, 1, 1, 1])
            cols[0].write(tanggal)
            cols[1].write(nama)
            cols[2].write(jumlah)
            cols[3].write(satuan)

            btn_edit, btn_delete = cols[4].columns([1, 1])
            with btn_edit:
                if st.button("✏️", key=f"edit_{id_keluar}", help="Edit"):
                    st.session_state.dialog_type = "edit"
                    st.session_state.active_record = record
            with btn_delete:
                if st.button("🗑️", key=f"delete_{id_keluar}", help="Hapus"):
                    st.session_state.dialog_type = "delete"
                    st.session_state.active_record = record

        # -----------------------------
        # Dialog Edit / Delete
        # -----------------------------
        @st.dialog("Form Data Bahan Baku Keluar")
        def universal_dialog(record, mode):
            id_keluar, nama, satuan, tanggal, jumlah, id_bahan_baku = record

            if mode == "edit":
                st.subheader("✏️ Edit Data")
                bahan_list = fetch_bahan_baku()
                bahan_dict = {f"{n} ({s})": i for i, n, s in bahan_list}
                current_option = f"{nama} ({satuan})"

                new_bahan = st.selectbox(
                    "Pilih Bahan Baku",
                    list(bahan_dict.keys()),
                    index=list(bahan_dict.keys()).index(current_option)
                )

                # Parse tanggal dengan benar
                try:
                    if isinstance(tanggal, str):
                        # Coba berbagai format tanggal
                        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                            try:
                                date_value = datetime.strptime(
                                    tanggal, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            date_value = datetime.now().date()
                    else:
                        date_value = tanggal
                except:
                    date_value = datetime.now().date()

                new_tanggal = st.date_input("Tanggal Keluar", value=date_value)
                new_jumlah = st.number_input(
                    "Jumlah Bahan Baku", min_value=0.0, step=0.1, value=float(jumlah))

                if st.button("💾 Simpan Perubahan"):
                    update_record(
                        id_keluar, (bahan_dict[new_bahan], str(new_tanggal), new_jumlah))
                    st.success("✅ Data berhasil diperbarui!")
                    st.session_state.dialog_type = None
                    st.session_state.active_record = None
                    st.rerun()

            elif mode == "delete":
                st.subheader("⚠️ Konfirmasi Penghapusan")
                st.warning(
                    f"Apakah Anda yakin ingin menghapus data **{nama} ({jumlah} {satuan})** pada tanggal **{tanggal}**?")
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

        # Jalankan dialog jika aktif
        if st.session_state.dialog_type and st.session_state.active_record:
            universal_dialog(st.session_state.active_record,
                             st.session_state.dialog_type)