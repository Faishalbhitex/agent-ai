import os
import json
from typing import List, Union

def load_retail_data():
    try:
        # Dapatkan path absolut ke file ini
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Gabungkan dengan nama file data
        data_path = os.path.join(base_dir, "retail_data.json")
        with open(data_path, "r") as f:
            harga_dagang = json.load(f)
        return harga_dagang
    except Exception as e:
        return None

# Fungsi untuk mendapatkan list nama produk saja pada tipe tertentu
def get_nama_produk(tipe_produk: str) -> dict[str, list]:
    harga_dagang = load_retail_data()
    if harga_dagang is None:
        return {"status": "error", "list_nama_produk": []}
    tipe_produk = tipe_produk.lower()
    if tipe_produk in harga_dagang:
        nama_produk_list = [produk["nama produk"] for produk in harga_dagang[tipe_produk]]
        return {"status": "success", "tipe_produk": tipe_produk, "list_nama_produk": nama_produk_list}
    else:
        return {"status": "error", "list_nama_produk": []}

def get_harga_dagang(tipe_produk: str, nama_produk: str) -> dict[str, str]:
    harga_dagang = load_retail_data()
    if harga_dagang is None:
        return {"status": "error", "message": f"Gagal membaca file data: retail_data.json"}
    tipe_produk = tipe_produk.lower()
    nama_produk = nama_produk.lower()
    if tipe_produk in harga_dagang:
        for produk in harga_dagang[tipe_produk]:
            if produk["nama produk"].lower() == nama_produk:
                return {
                    "status": "success",
                    "tipe_produk": tipe_produk,
                    "nama_produk": produk["nama produk"],
                    "harga encer": produk["harga encer"]
                }
        return {"status": "error", "message": f"Nama produk '{nama_produk}' tidak ditemukan pada tipe '{tipe_produk}'"}
    else:
        return {"status": "error", "message": f"Tipe produk '{tipe_produk}' tidak ditemukan"}

# Fungsi untuk mendapatkan list nama produk beserta harga pada tipe tertentu
def get_list_type_produk_nama_dan_harga(tipe_produk: str) -> dict[str, list]:
    harga_dagang = load_retail_data()
    if harga_dagang is None:
        return {"status": "error", "list_produk": []}
    tipe_produk = tipe_produk.lower()
    if tipe_produk in harga_dagang:
        produk_list = [
            {"nama_produk": produk["nama produk"], "harga": produk["harga encer"]}
            for produk in harga_dagang[tipe_produk]
        ]
        return {"status": "success", "tipe_produk": tipe_produk, "list_produk": produk_list}
    else:
        return {"status": "error", "list_produk": []}

def get_list_tipe_produk() -> dict[str, list]:
    harga_dagang = load_retail_data()
    if harga_dagang is None:
        return {"status": "error", "list_tipe_produk": []}
    tipe_produk_list = list(harga_dagang.keys())
    return {"status": "success", "list_tipe_produk": tipe_produk_list}

def update_harga_dagang(
    tipe_produk: str,
    nama_produk: list[str],
    harga_dagang_baru: list[str]
) -> dict[str, list]:
    """
    Mengupdate harga satu atau beberapa produk.

    Args:
        tipe_produk (str): Nama tipe produk.
        nama_produk (List[str]): Daftar nama produk.
        harga_dagang_baru (List[str]): Daftar harga baru.

    Returns:
        dict[str, list]: Status dan hasil update.
    """
    data = load_retail_data()
    if data is None:
        return {"status": "error", "results": ["Gagal membaca file data: retail_data.json"]}
    tipe_produk = tipe_produk.lower()
    if len(nama_produk) != len(harga_dagang_baru):
        return {"status": "error", "results": ["Jumlah nama produk dan harga baru harus sama"]}
    results = []
    if tipe_produk in data:
        for n, h in zip(nama_produk, harga_dagang_baru):
            n_l = n.lower()
            found = False
            for produk in data[tipe_produk]:
                if produk["nama produk"].lower() == n_l:
                    produk["harga encer"] = h
                    found = True
                    results.append(f"Harga produk '{n}' berhasil diupdate menjadi {h}")
                    break
            if not found:
                results.append(f"Nama produk '{n}' tidak ditemukan pada tipe '{tipe_produk}'")
        # Simpan perubahan jika ada yang berhasil
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, "retail_data.json")
            with open(data_path, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            return {"status": "error", "results": [f"Gagal menyimpan perubahan: {e}"]}
        return {"status": "multi", "results": results}
    else:
        return {"status": "error", "results": [f"Tipe produk '{tipe_produk}' tidak ditemukan"]}

def change_nama_produk(tipe_produk: str, nama_produk: str, nama_produk_baru: str) -> dict[str, str]:
    data = load_retail_data()
    if data is None:
        return {"status": "error", "message": f"Gagal membaca file data: retail_data.json"}
    tipe_produk = tipe_produk.lower()
    nama_produk = nama_produk.lower()
    if tipe_produk in data:
        for produk in data[tipe_produk]:
            if produk["nama produk"].lower() == nama_produk:
                produk["nama produk"] = nama_produk_baru
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    data_path = os.path.join(base_dir, "retail_data.json")
                    with open(data_path, "w") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return {"status": "success", "message": f"Nama produk berhasil diubah menjadi '{nama_produk_baru}'"}
                except Exception as e:
                    return {"status": "error", "message": f"Gagal menyimpan perubahan: {e}"}
        return {"status": "error", "message": f"Nama produk '{nama_produk}' tidak ditemukan pada tipe '{tipe_produk}'"}
    else:
        return {"status": "error", "message": f"Tipe produk '{tipe_produk}' tidak ditemukan"}

def add_produk(
    tipe_produk: str,
    nama_produk: list[str],
    harga_dagang: list[str]
) -> dict[str, list]:
    """
    Menambah satu atau beberapa produk baru ke tipe produk tertentu.

    Args:
        tipe_produk (str): Nama tipe produk.
        nama_produk (List[str]): Daftar nama produk.
        harga_dagang (List[str]): Daftar harga produk.

    Returns:
        dict[str, list]: Status dan hasil penambahan produk.
    """
    data = load_retail_data()
    if data is None:
        return {"status": "error", "results": ["Gagal membaca file data: retail_data.json"]}
    tipe_produk = tipe_produk.lower()
    if len(nama_produk) != len(harga_dagang):
        return {"status": "error", "results": ["Jumlah nama produk dan harga harus sama"]}
    if tipe_produk not in data:
        return {"status": "error", "results": [f"Tipe produk '{tipe_produk}' tidak ditemukan"]}
    results = []
    for n, h in zip(nama_produk, harga_dagang):
        # Cek duplikasi nama produk
        if any(produk["nama produk"].lower() == n.lower() for produk in data[tipe_produk]):
            results.append(f"Produk '{n}' sudah ada pada tipe '{tipe_produk}'")
            continue
        data[tipe_produk].append({
            "nama produk": n,
            "harga encer": h
        })
        results.append(f"Produk '{n}' berhasil ditambahkan ke tipe '{tipe_produk}' dengan harga {h}")
    # Simpan perubahan jika ada yang berhasil
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "retail_data.json")
        with open(data_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        return {"status": "error", "results": [f"Gagal menyimpan perubahan: {e}"]}
    return {"status": "multi", "results": results}

# Fungsi untuk menghapus produk tertentu pada tipe tertentu
def delete_produk(tipe_produk: str, nama_produk: str) -> dict[str, str]:
    data = load_retail_data()
    if data is None:
        return {"status": "error", "message": f"Gagal membaca file data: retail_data.json"}
    tipe_produk = tipe_produk.lower()
    nama_produk = nama_produk.lower()
    if tipe_produk in data:
        produk_list = data[tipe_produk]
        for i, produk in enumerate(produk_list):
            if produk["nama produk"].lower() == nama_produk:
                del produk_list[i]
                try:
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    data_path = os.path.join(base_dir, "retail_data.json")
                    with open(data_path, "w") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return {"status": "success", "message": f"Produk '{produk['nama produk']}' berhasil dihapus dari tipe '{tipe_produk}'"}
                except Exception as e:
                    return {"status": "error", "message": f"Gagal menyimpan perubahan: {e}"}
        return {"status": "error", "message": f"Nama produk '{nama_produk}' tidak ditemukan pada tipe '{tipe_produk}'"}
    else:
        return {"status": "error", "message": f"Tipe produk '{tipe_produk}' tidak ditemukan"}