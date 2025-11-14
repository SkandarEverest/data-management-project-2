# SIX MongoDB Seeder

Project kecil untuk mensimulasikan **Sistem Informasi Akademik** menggunakan **MongoDB**, dengan data dummy yang di-generate oleh **Python + Faker**.

Skema awal berasal dari DDL PostgreSQL (tabel: `mahasiswa`, `dosen`, `fakultas`, `kurikulum`, `rencana_studi`, dsb), lalu dimapping menjadi struktur **dokumen MongoDB** (subdokumen & embedded arrays) yang lebih natural untuk NoSQL.

---

## 1. Teknologi yang Dipakai

- Python 3.11
- MongoDB (Docker)
- PyMongo
- Faker (id_ID)
- Pydantic

---

## 2. Struktur Folder

```
project2/
├─ db.py               # helper koneksi MongoDB
├─ models.py           # Pydantic models
├─ seed_data.py        # seluruh fungsi seed_*
├─ main_seed.py        # entry point untuk menjalankan semua seed
├─ docker-compose.yml  # compose untuk mongodb
├─ requirements.txt
├─ .env
├─ .gitignore
└─ README.md
```

---

## 3. Cara Menjalankan

### 3.1 Setup
```
create .env file based on .env.example
python -m pip install -r requirements.txt
```

### 3.2 Jalankan MongoDB (Docker)
```
docker compose up -d
```

### 3.3 Jalankan Seeder
```
python main_seed.py
```

Seeder akan otomatis:
- menghapus koleksi lama
- membuat data baru (fakultas, prodi, dosen, mahasiswa, kurikulum, jadwal, dll.)
- menginsert data skala besar sesuai konfigurasi di `seed_data.py`

---

## 4. Mengatur Skala Data

Jumlah data dapat diubah melalui konstanta di awal `seed_data.py`:

```
NUM_FAKULTAS = 13
NUM_PRODI = 140
NUM_DOSEN = 3540
NUM_MAHASISWA = 33296
NUM_RUANGAN = 150
```

---
