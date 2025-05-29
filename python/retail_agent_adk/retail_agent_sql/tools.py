"""
Tools SQL untuk Agent Retail AI - Faishal Bhitex
Berisi fungsi-fungsi CRUD SQLite yang cepat dan efisien
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailSQLTools:
    """Tools SQL untuk operasi database retail yang cepat dan efisien"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "database", "db_retail.db")
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def get_connection(self) -> sqlite3.Connection:
        """Membuat koneksi database dengan optimasi performa"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging untuk performa
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        return conn

def lihat_semua_produk(limit: Optional[int] = None, offset: int = 0) -> str:
    """
    Melihat semua produk dalam database retail.
    
    Args:
        limit (int, optional): Jumlah maksimum produk yang ditampilkan. Default: semua.
        offset (int): Mulai dari record ke-berapa. Default: 0.
    
    Returns:
        str: JSON string berisi daftar produk atau pesan error.
        
    Example:
        - lihat_semua_produk(10) -> 10 produk pertama
        - lihat_semua_produk(5, 10) -> 5 produk mulai dari record ke-10
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        
        query = "SELECT * FROM retail_products ORDER BY id"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return json.dumps({"status": "success", "message": "Tidak ada produk ditemukan", "data": []})
        
        result = {
            "status": "success",
            "total_shown": len(df),
            "data": df.to_dict('records')
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error lihat_semua_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal mengambil data produk: {str(e)}"})

def cari_produk(keyword: str, kolom: str = "nama_produk") -> str:
    """
    Mencari produk berdasarkan keyword di kolom tertentu.
    
    Args:
        keyword (str): Kata kunci pencarian.
        kolom (str): Kolom yang dicari ('nama_produk', 'type_produk', 'harga_encer'). Default: 'nama_produk'.
    
    Returns:
        str: JSON string berisi hasil pencarian.
        
    Example:
        - cari_produk("rokok") -> cari di nama_produk
        - cari_produk("15000", "harga_encer") -> cari di harga_encer
    """
    try:
        valid_columns = ['nama_produk', 'type_produk', 'harga_encer']
        if kolom not in valid_columns:
            return json.dumps({"status": "error", "message": f"Kolom harus salah satu dari: {valid_columns}"})
            
        tools = RetailSQLTools()
        conn = tools.get_connection()
        
        query = f"SELECT * FROM retail_products WHERE {kolom} LIKE ? ORDER BY id"
        df = pd.read_sql_query(query, conn, params=[f'%{keyword}%'])
        conn.close()
        
        result = {
            "status": "success",
            "keyword": keyword,
            "kolom_pencarian": kolom,
            "jumlah_ditemukan": len(df),
            "data": df.to_dict('records')
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error cari_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal mencari produk: {str(e)}"})

def lihat_berdasarkan_kategori(type_produk: str) -> str:
    """
    Melihat semua produk berdasarkan kategori/type tertentu.
    
    Args:
        type_produk (str): Kategori produk yang ingin dilihat.
    
    Returns:
        str: JSON string berisi produk dalam kategori tersebut.
        
    Example:
        - lihat_berdasarkan_kategori("jenis rokok")
        - lihat_berdasarkan_kategori("produk isi ulang")
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        
        df = pd.read_sql_query(
            "SELECT * FROM retail_products WHERE type_produk = ? ORDER BY nama_produk",
            conn, params=[type_produk]
        )
        conn.close()
        
        result = {
            "status": "success",
            "kategori": type_produk,
            "jumlah_produk": len(df),
            "data": df.to_dict('records')
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error lihat_berdasarkan_kategori: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal mengambil data kategori: {str(e)}"})

def tambah_produk(nama_produk: str, harga_encer: str, type_produk: str, tanggal: Optional[str] = None) -> str:
    """
    Menambahkan produk baru ke database.
    
    Args:
        nama_produk (str): Nama produk yang akan ditambahkan.
        harga_encer (str): Harga produk (format: "Rp.15.000").
        type_produk (str): Kategori/type produk.
        tanggal (str, optional): Tanggal ditambahkan (YYYY-MM-DD). Default: hari ini.
    
    Returns:
        str: JSON string konfirmasi penambahan produk.
        
    Example:
        - tambah_produk("Indomie Goreng", "Rp.3.500", "makanan instant")
    """
    try:
        if not nama_produk or not harga_encer or not type_produk:
            return json.dumps({"status": "error", "message": "Nama produk, harga, dan type produk harus diisi"})
        tanggal = datetime.now().strftime('%Y-%m-%d')
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO retail_products (nama_produk, harga_encer, type_produk, tanggal_ditambah)
            VALUES (?, ?, ?, ?)
        ''', (nama_produk, harga_encer, type_produk, tanggal))
        conn.commit()
        produk_id = cursor.lastrowid
        conn.close()
        result = {
            "status": "success",
            "message": "Produk berhasil ditambahkan",
            "data": {
                "id": produk_id,
                "nama_produk": nama_produk,
                "harga_encer": harga_encer,
                "type_produk": type_produk,
                "tanggal_ditambah": tanggal
            }
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error tambah_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal menambah produk: {str(e)}"})

def tambah_multiple_produk(list_produk: str) -> str:
    """
    Menambahkan beberapa produk sekaligus untuk efisiensi.
    
    Args:
        list_produk (str): JSON string berisi list produk yang akan ditambahkan.
                          Format: '[{"nama": "...", "harga": "...", "type": "..."}, ...]'
    
    Returns:
        str: JSON string konfirmasi penambahan multiple produk.
        
    Example:
        - tambah_multiple_produk('[{"nama": "Teh Botol", "harga": "Rp.5.000", "type": "minuman"}]')
    """
    try:
        produk_data = json.loads(list_produk)
        if not isinstance(produk_data, list):
            return json.dumps({"status": "error", "message": "Data harus berupa array/list produk"})
        tanggal = datetime.now().strftime('%Y-%m-%d')
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        data_insert = []
        for produk in produk_data:
            if not all(key in produk for key in ['nama', 'harga', 'type']):
                continue
            data_insert.append((produk['nama'], produk['harga'], produk['type'], tanggal))
        cursor.executemany('''
            INSERT INTO retail_products (nama_produk, harga_encer, type_produk, tanggal_ditambah)
            VALUES (?, ?, ?, ?)
        ''', data_insert)
        conn.commit()
        conn.close()
        result = {
            "status": "success",
            "message": f"Berhasil menambahkan {len(data_insert)} produk",
            "jumlah_ditambahkan": len(data_insert),
            "tanggal": tanggal
        }
        return json.dumps(result, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Format JSON tidak valid"})
    except Exception as e:
        logger.error(f"Error tambah_multiple_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal menambah multiple produk: {str(e)}"})

def update_produk(produk_id: int, nama_produk: Optional[str] = None, 
                  harga_encer: Optional[str] = None, type_produk: Optional[str] = None) -> str:
    """
    Mengupdate data produk berdasarkan ID.
    
    Args:
        produk_id (int): ID produk yang akan diupdate.
        nama_produk (str, optional): Nama produk baru.
        harga_encer (str, optional): Harga baru.
        type_produk (str, optional): Type/kategori baru.
    
    Returns:
        str: JSON string konfirmasi update.
        
    Example:
        - update_produk(1, harga_encer="Rp.4.000") -> update harga saja
        - update_produk(1, nama_produk="Indomie Ayam Bawang", harga_encer="Rp.3.500")
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        updates = []
        params = []
        if nama_produk:
            updates.append("nama_produk = ?")
            params.append(nama_produk)
        if harga_encer:
            updates.append("harga_encer = ?")
            params.append(harga_encer)
        if type_produk:
            updates.append("type_produk = ?")
            params.append(type_produk)
        tanggal = datetime.now().strftime('%Y-%m-%d')
        if updates:
            updates.append("tanggal_ditambah = ?")
            params.append(tanggal)
        if not updates:
            return json.dumps({"status": "error", "message": "Tidak ada data yang diupdate"})
        params.append(produk_id)
        query = f"UPDATE retail_products SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        if cursor.rowcount > 0:
            cursor.execute("SELECT * FROM retail_products WHERE id = ?", [produk_id])
            updated_data = cursor.fetchone()
            conn.close()
            result = {
                "status": "success",
                "message": f"Produk ID {produk_id} berhasil diupdate",
                "data": {
                    "id": updated_data[0],
                    "nama_produk": updated_data[1],
                    "harga_encer": updated_data[2],
                    "type_produk": updated_data[3],
                    "tanggal_ditambah": updated_data[4]
                }
            }
            return json.dumps(result, ensure_ascii=False)
        else:
            conn.close()
            return json.dumps({"status": "error", "message": f"Produk dengan ID {produk_id} tidak ditemukan"})
    except Exception as e:
        logger.error(f"Error update_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal update produk: {str(e)}"})

def update_harga_massal(type_produk: str, persentase_kenaikan: float) -> str:
    """
    Update harga secara massal berdasarkan kategori dengan persentase kenaikan.
    
    Args:
        type_produk (str): Kategori produk yang akan diupdate harganya.
        persentase_kenaikan (float): Persentase kenaikan harga (contoh: 10.0 untuk 10%).
    
    Returns:
        str: JSON string konfirmasi update massal.
        
    Example:
        - update_harga_massal("jenis rokok", 15.0) -> naik 15%
        - update_harga_massal("minuman", -5.0) -> turun 5%
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_produk, harga_encer FROM retail_products WHERE type_produk = ?", [type_produk])
        products = cursor.fetchall()
        if not products:
            conn.close()
            return json.dumps({"status": "error", "message": f"Tidak ada produk dengan kategori: {type_produk}"})
        updated_products = []
        updated_count = 0
        tanggal = datetime.now().strftime('%Y-%m-%d')
        for product_id, nama, harga_str in products:
            try:
                harga_angka = int(''.join(filter(str.isdigit, harga_str)))
                harga_baru = int(harga_angka * (1 + persentase_kenaikan/100))
                harga_baru_str = f"Rp.{harga_baru:,}".replace(',', '.')
                cursor.execute("UPDATE retail_products SET harga_encer = ?, tanggal_ditambah = ? WHERE id = ?", 
                             [harga_baru_str, tanggal, product_id])
                updated_products.append({
                    "id": product_id,
                    "nama_produk": nama,
                    "harga_lama": harga_str,
                    "harga_baru": harga_baru_str,
                    "tanggal_ditambah": tanggal
                })
                updated_count += 1
            except ValueError:
                continue
        conn.commit()
        conn.close()
        result = {
            "status": "success",
            "message": f"Berhasil update {updated_count} produk kategori '{type_produk}'",
            "kategori": type_produk,
            "persentase_kenaikan": persentase_kenaikan,
            "jumlah_diupdate": updated_count,
            "detail_produk": updated_products
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error update_harga_massal: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal update harga massal: {str(e)}"})

def hapus_produk(produk_id: int) -> str:
    """
    Menghapus produk berdasarkan ID.
    
    Args:
        produk_id (int): ID produk yang akan dihapus.
    
    Returns:
        str: JSON string konfirmasi penghapusan.
        
    Example:
        - hapus_produk(15) -> hapus produk dengan ID 15
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        
        # Get data sebelum dihapus
        cursor.execute("SELECT * FROM retail_products WHERE id = ?", [produk_id])
        deleted_data = cursor.fetchone()
        
        if not deleted_data:
            conn.close()
            return json.dumps({"status": "error", "message": f"Produk dengan ID {produk_id} tidak ditemukan"})
        
        cursor.execute("DELETE FROM retail_products WHERE id = ?", [produk_id])
        conn.commit()
        conn.close()
        
        result = {
            "status": "success",
            "message": f"Produk ID {produk_id} berhasil dihapus",
            "data_terhapus": {
                "id": deleted_data[0],
                "nama_produk": deleted_data[1],
                "harga_encer": deleted_data[2],
                "type_produk": deleted_data[3],
                "tanggal_ditambah": deleted_data[4]
            }
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error hapus_produk: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal menghapus produk: {str(e)}"})

def hapus_berdasarkan_kategori(type_produk: str) -> str:
    """
    Menghapus semua produk berdasarkan kategori/type.
    
    Args:
        type_produk (str): Kategori produk yang akan dihapus semua.
    
    Returns:
        str: JSON string konfirmasi penghapusan massal.
        
    Example:
        - hapus_berdasarkan_kategori("produk rusak")
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        cursor = conn.cursor()
        
        # Count berapa yang akan dihapus
        cursor.execute("SELECT COUNT(*) FROM retail_products WHERE type_produk = ?", [type_produk])
        count_to_delete = cursor.fetchone()[0]
        
        if count_to_delete == 0:
            conn.close()
            return json.dumps({"status": "error", "message": f"Tidak ada produk dengan kategori: {type_produk}"})
        
        cursor.execute("DELETE FROM retail_products WHERE type_produk = ?", [type_produk])
        conn.commit()
        conn.close()
        
        result = {
            "status": "success",
            "message": f"Berhasil menghapus {count_to_delete} produk kategori '{type_produk}'",
            "kategori": type_produk,
            "jumlah_dihapus": count_to_delete
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error hapus_berdasarkan_kategori: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal menghapus berdasarkan kategori: {str(e)}"})

def statistik_database() -> str:
    """
    Mendapatkan statistik lengkap database retail.
    
    Returns:
        str: JSON string berisi statistik database.
        
    Example:
        Menampilkan total produk, kategori, distribusi harga, dll.
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        
        # Total produk
        total_query = "SELECT COUNT(*) as total FROM retail_products"
        total_df = pd.read_sql_query(total_query, conn)
        total_produk = total_df.iloc[0]['total']
        
        # Produk per kategori
        kategori_query = """
            SELECT type_produk, COUNT(*) as jumlah 
            FROM retail_products 
            GROUP BY type_produk 
            ORDER BY jumlah DESC
        """
        kategori_df = pd.read_sql_query(kategori_query, conn)
        
        # Produk terbaru
        terbaru_query = """
            SELECT nama_produk, type_produk, harga_encer, tanggal_ditambah 
            FROM retail_products 
            ORDER BY id DESC 
            LIMIT 5
        """
        terbaru_df = pd.read_sql_query(terbaru_query, conn)
        
        conn.close()
        
        result = {
            "status": "success",
            "statistik": {
                "total_produk": int(total_produk),
                "jumlah_kategori": len(kategori_df),
                "distribusi_kategori": kategori_df.to_dict('records'),
                "produk_terbaru": terbaru_df.to_dict('records')
            }
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error statistik_database: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal mendapatkan statistik: {str(e)}"})

def daftar_kategori() -> str:
    """
    Mendapatkan daftar semua kategori/type produk yang ada.
    
    Returns:
        str: JSON string berisi daftar kategori.
        
    Example:
        Menampilkan semua kategori produk yang tersedia.
    """
    try:
        tools = RetailSQLTools()
        conn = tools.get_connection()
        
        query = """
            SELECT type_produk, COUNT(*) as jumlah_produk 
            FROM retail_products 
            GROUP BY type_produk 
            ORDER BY type_produk
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        result = {
            "status": "success",
            "total_kategori": len(df),
            "daftar_kategori": df.to_dict('records')
        }
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error daftar_kategori: {str(e)}")
        return json.dumps({"status": "error", "message": f"Gagal mendapatkan daftar kategori: {str(e)}"})

# Daftar semua tools yang tersedia untuk agent
AVAILABLE_TOOLS = [
    lihat_semua_produk,
    cari_produk, 
    lihat_berdasarkan_kategori,
    tambah_produk,
    tambah_multiple_produk,
    update_produk,
    update_harga_massal,
    hapus_produk,
    hapus_berdasarkan_kategori,
    statistik_database,
    daftar_kategori
]