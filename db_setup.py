import streamlit as st
import sqlite3


def init_db():
    con = sqlite3.connect("inventory.db")
    cur = con.cursor()


    cur.execute("""
        CREATE TABLE IF NOT EXISTS stok_bahan_baku (
            id_bahan_baku INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_bahan_baku TEXT NOT NULL,
            satuan_bahan_baku TEXT NOT NULL,
            lead_time INTEGER DEFAULT 0,
            biaya_pesan INTEGER DEFAULT 0,
            biaya_simpan INTEGER DEFAULT 0
        )
    """)



    # tabel stok barang jadi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stok_barang_jadi (
            id_barang_jadi INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_barang_jadi TEXT NOT NULL,
            grade_barang_jadi TEXT NOT NULL,
            satuan_barang_jadi TEXT NOT NULL,
            harga_barang_jadi INTEGER
        )
    """)
    
    # tabel bahan baku masuk
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bahan_baku_masuk (
            id_masuk INTEGER PRIMARY KEY AUTOINCREMENT,
            id_bahan_baku INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            jumlah_bahan_baku REAL NOT NULL,
            FOREIGN KEY (id_bahan_baku) REFERENCES stok_bahan_baku(id_bahan_baku)
        )
    """)

    # tabel bahan baku keluar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bahan_baku_keluar (
            id_keluar INTEGER PRIMARY KEY AUTOINCREMENT,
            id_bahan_baku INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            jumlah_bahan_baku REAL NOT NULL,
            FOREIGN KEY (id_bahan_baku) REFERENCES stok_bahan_baku(id_bahan_baku)
        )
    """)

    # tabel produk jadi masuk
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produk_jadi_masuk (
            id_masuk INTEGER PRIMARY KEY AUTOINCREMENT,
            id_barang_jadi INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            jumlah_barang_jadi REAL NOT NULL,
            FOREIGN KEY (id_barang_jadi) REFERENCES stok_barang_jadi(id_barang_jadi)
        )
    """)

    # tabel produk jadi keluar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS produk_jadi_keluar (
            id_keluar INTEGER PRIMARY KEY AUTOINCREMENT,
            id_barang_jadi INTEGER NOT NULL,
            tanggal TEXT NOT NULL,
            jumlah_barang_jadi REAL NOT NULL,
            FOREIGN KEY (id_barang_jadi) REFERENCES stok_barang_jadi(id_barang_jadi)
        )
    """)

    con.commit()
    con.close()