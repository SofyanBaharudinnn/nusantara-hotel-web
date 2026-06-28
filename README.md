# Nusantara Hospitality Group - Data Analytics & Warehouse Portal

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.1-red.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20MySQL-lightgrey.svg)](https://www.sqlite.org/)
[![Security](https://img.shields.io/badge/Security-CSRF%20%26%20Rate%20Limit-green.svg)](https://flask-wtf.readthedocs.io/)
[![Frontend](https://img.shields.io/badge/Frontend-Three.js%20%26%20Chart.js-orange.svg)](https://threejs.org/)

Platform Intelijen Bisnis (BI) terpadu untuk memonitor, menganalisis, dan memaksimalkan potensi operasional hotel, resor, dan properti di bawah naungan **Nusantara Hospitality Group**. Sistem ini menghubungkan database Data Warehouse transaksional dengan antarmuka visual modern berbasis web.

Proyek ini dikembangkan oleh **Kelompok 2** sebagai tugas akhir mata kuliah **Data Warehouse & OLAP** di **Universitas Musamus Merauke**.

---

## 🌟 Fitur Utama

### 1. Visualisasi Peta 3D Indonesia (Landing Page)
* **Peta Interaktif**: Render peta kepulauan Indonesia secara 3D menggunakan **Three.js** dan WebGL.
* **Desain Modern**: Garis tepi pulau (*neon glowing outlines*) meliputi pulau Sumatera, Jawa, Kalimantan, Sulawesi, Papua, dan Nusa Tenggara.
* **Lokasi Operasional**: Pin operasional 3D dengan label nama kota (billboard text) pada hub utama: **Medan, Jakarta, Surabaya, Makassar, dan Jayapura**.
* **Visualisasi Alur Data**: Efek aliran data dinamis (*arc curves*) dengan partikel bergerak berwarna emas yang menghubungkan antar hub utama untuk merepresentasikan transfer informasi/reservasi.

### 2. Dashboard Analitik & Visualisasi Data
Sistem menyediakan dua level dashboard berdasarkan peran pengguna:
* **Dashboard Admin**: Akses penuh ke seluruh matriks, filter interaktif, serta kemampuan memodifikasi data.
* **Dashboard User**: Akses read-only ke visualisasi analitik.
* **Indikator Kunci (KPIs)**:
  * **Total Reservasi**: Total pemesanan kamar terdaftar.
  * **Total Pendapatan (Revenue)**: Pendapatan kotor dari reservasi aktif.
  * **Rata-rata Durasi Inap (Avg Nights)**: Durasi menginap rata-rata per reservasi.
  * **Jumlah Tamu Unik**: Total tamu yang terdaftar di database.
  * **Persentase Pembatalan (Cancel Rate)**: Rasio pesanan yang dibatalkan terhadap total pesanan.
* **Grafik Visualisasi Interaktif (Chart.js)**:
  * **Tren Pendapatan & Okupansi**: Grafik kuartalan tren hunian per tipe hotel (City Hotel vs Resort Hotel).
  * **Distribusi Booking Channel**: Diagram lingkaran alur pemesanan (Direct, OTA, Agent).
  * **Segmentasi Tamu**: Analisis tipe segmen pasar (Corporate, Aviation, Online TA, Groups, dsb).
  * **Statistik Lainnya**: Tren musiman pendapatan, tipe kamar terlaris, asal negara tamu teratas, serta tabel data reservasi terbaru.

### 3. Keamanan Tingkat Tinggi (Security Hardening)
* **Proteksi CSRF**: Penerapan token CSRF (`Flask-WTF`) secara global di setiap form POST untuk melindungi dari serangan pemalsuan permintaan lintas situs.
* **Rate Limiting**: Batasan frekuensi request (`Flask-Limiter`) pada rute sensitif guna mencegah serangan brute force dan DoS:
  * `/login` dibatasi maksimal **5 request per menit**.
  * `/register` dibatasi maksimal **3 request per menit**.
* **Skrip Pengujian Keamanan**: Menyertakan file `test_security.py` untuk menguji fungsionalitas CSRF protection dan rate limiting secara otomatis.

### 4. Ekspor Laporan Terintegrasi (Data Export)
* Dukungan pengunduhan laporan data reservasi, okupansi, kamar, dan customer secara langsung ke format **Excel (.xlsx)** atau **CSV (.csv)**.
* Proses ekspor diolah di sisi backend dengan performa tinggi menggunakan pustaka `pandas` dan `openpyxl`.

### 5. Manajemen Pengguna (User CRUD)
* Dashboard kontrol eksklusif bagi Administrator untuk melakukan pengelolaan akun:
  * Menambah user baru.
  * Mengedit kredensial (username, email, password) dan mengubah peran (*role*: Admin / User).
  * Menghapus user sistem analitik (dilengkapi validasi agar admin tidak dapat menghapus akunnya sendiri yang sedang aktif).

### 6. Pengelolaan Data Warehouse (Data CRUD)
* Fitur manipulasi data langsung pada tabel dimensi Data Warehouse untuk:
  * **Tamu / Customers** (`dim_guest`)
  * **Kamar / Rooms** (`dim_room`)
  * **Properti Hotel & Okupansi** (`dim_hotel`)
* Mendukung operasi **Update** dan **Delete** dengan mekanisme cascade delete otomatis pada tabel fakta `fact_reservation` untuk menjaga integritas referensial data.

---

## 🛠️ Tech Stack

* **Backend**: Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF, Flask-Limiter
* **Database**: 
  * **SQLite**: Digunakan secara default untuk kemudahan portabilitas & free hosting.
  * **MySQL / MariaDB**: Didukung untuk implementasi berskala enterprise.
* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & Neon Dark Theme), JavaScript (ES6)
* **Libraries**: Three.js (3D Map), Chart.js (Interactive Charts), Pandas, OpenPyXL (Excel Generator), PyMySQL (MySQL Driver)

---

## 📂 Struktur Direktori Project

```text
nusantara-hotel-web/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py              # Model SQLAlchemy untuk akun pengguna (SQLite)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin.py             # Rute dashboard admin, CRUD DW, ekspor & manajemen user
│   │   ├── auth.py              # Rute login, register (dengan Rate Limiter), logout
│   │   ├── main.py              # Rute landing page & render peta 3D
│   │   └── user.py              # Rute dashboard user biasa (read-only)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Desain Glassmorphism & Neon Dark Theme
│   │   └── js/
│   │       ├── main.js          # Inisialisasi peta 3D menggunakan Three.js
│   │       └── map_data.js      # Titik koordinat dan data hub regional Indonesia
│   ├── templates/
│   │   ├── admin/               # Template tampilan khusus administrator
│   │   │   ├── customer.html
│   │   │   ├── dashboard.html
│   │   │   ├── kelola_user.html
│   │   │   ├── okupansi.html
│   │   │   └── room.html
│   │   ├── user/                # Template tampilan khusus user biasa
│   │   │   ├── _sidebar.html
│   │   │   ├── customer.html
│   │   │   ├── dashboard.html
│   │   │   ├── okupansi.html
│   │   │   ├── room.html
│   │   │   └── seasonal.html
│   │   ├── base.html            # Layout utama aplikasi
│   │   ├── landing.html         # Landing page dengan peta 3D
│   │   └── login.html           # Halaman login/register dengan transisi mulus
│   ├── utils/
│   │   └── queries.py           # Kumpulan fungsi SQL Query untuk dashboard & ekspor
│   └── __init__.py              # Inisialisasi aplikasi Flask & ekstensi
├── instance/
│   └── dw_hospitality.db        # Database SQLite Data Warehouse (Tabel fakta & dimensi)
├── .env                         # Konfigurasi environment variables
├── build.sh                     # Script build untuk deploy deployment otomatis
├── config.py                    # Konfigurasi class Flask
├── convert_to_sqlite.py         # Script utilitas migrasi data dari MySQL ke SQLite
├── dump_mysql.py                # Script backup schema dan data MySQL ke file .sql
├── Procfile                     # Konfigurasi server untuk platform deployment (Gunicorn/Web)
├── README.md                    # Dokumentasi utama proyek
├── requirements.txt             # Daftar pustaka dependensi Python
├── run.py                       # Titik masuk utama aplikasi (Entrypoint)
└── test_security.py             # Script pengujian proteksi CSRF dan Rate Limiting
```

---

## 📊 Skema Basis Data (Data Warehouse)

Proyek ini menerapkan perancangan **Star Schema** untuk Data Warehouse Hospitality:

```mermaid
erDiagram
    dim_guest {
        int guest_key PK
        string guest_name
        string nationality
        string segment
        string city
    }
    dim_room {
        int room_key PK
        string room_type
        int capacity
        float base_rate
    }
    dim_hotel {
        int hotel_key PK
        string hotel_name
        string hotel_type
        string city
    }
    dim_time {
        int date_key PK
        date full_date
        int year
        int quarter
        int month
        int day
    }
    dim_booking_channel {
        int channel_key PK
        string channel_name
        string channel_type
    }
    fact_reservation {
        int reservation_key PK
        int date_key FK
        int guest_key FK
        int hotel_key FK
        int room_key FK
        int channel_key FK
        int nights
        int rooms_booked
        float room_revenue
        string is_cancelled
    }

    fact_reservation ||--o{ dim_guest : "guest_key"
    fact_reservation ||--o{ dim_room : "room_key"
    fact_reservation ||--o{ dim_hotel : "hotel_key"
    fact_reservation ||--o{ dim_time : "date_key"
    fact_reservation ||--o{ dim_booking_channel : "channel_key"
```

---

## 💻 Panduan Instalasi Lokal

### 1. Prasyarat
Pastikan komputer Anda sudah terpasang:
* [Python 3.10 atau versi terbaru](https://www.python.org/downloads/)
* Database MySQL (opsional jika ingin menggunakan MySQL secara penuh, misal melalui XAMPP atau Laragon).

### 2. Kloning Project
```bash
git clone https://github.com/SofyanBaharudinnn/nusantara-hotel-web.git
cd nusantara-hotel-web
```

### 3. Buat Virtual Environment & Install Dependencies
**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Konfigurasi Environment (`.env`)
Buat file bernama `.env` di root direktori proyek, lalu isi dengan konfigurasi berikut:
```ini
SECRET_KEY=nusantara-super-secret-key-2024
DATABASE_URL=sqlite:///users.db
DW_DATABASE_URL=sqlite:///instance/dw_hospitality.db
FLASK_ENV=development
FLASK_DEBUG=1
```
> [!NOTE]
> Secara default, aplikasi dikonfigurasi menggunakan SQLite untuk database pengguna (`users.db`) dan database Data Warehouse (`dw_hospitality.db` di folder `instance/`) agar aplikasi dapat langsung berjalan tanpa instalasi database eksternal.

Jika Anda ingin menggunakan **MySQL** untuk Data Warehouse, ubah `DW_DATABASE_URL` menjadi:
```ini
DW_DATABASE_URL=mysql+pymysql://username:password@localhost:3306/dw_hospitality
```

### 5. Jalankan Aplikasi
```bash
python run.py
```
Buka browser Anda dan akses: [**`http://127.0.0.1:5000`**](http://127.0.0.1:5000)

---

## 🛠️ Script Utilitas Database

### A. Migrasi MySQL ke SQLite (`convert_to_sqlite.py`)
Jika Anda memiliki data di database MySQL lokal dan ingin memindahkannya ke SQLite untuk kebutuhan deployment ringan, jalankan:
```bash
python convert_to_sqlite.py
```
Script ini akan membaca semua tabel dimensi dan fakta dari MySQL, kemudian menyalin datanya ke file database SQLite baru di `instance/dw_hospitality.db`.

### B. Backup MySQL ke File SQL (`dump_mysql.py`)
Untuk melakukan backup skema database dan semua data records MySQL lokal ke file `backup_dw.sql`, jalankan:
```bash
python dump_mysql.py
```

---

## 🔒 Pengujian Keamanan (Security Testing)

Untuk memverifikasi proteksi keamanan seperti **CSRF Protection** dan **Rate Limiting** berjalan dengan baik, jalankan script pengujian keamanan berikut saat aplikasi lokal Flask sedang aktif:

1. Pastikan server lokal menyala (`python run.py` di terminal pertama).
2. Buka terminal baru, aktifkan venv, lalu jalankan:
   ```bash
   python test_security.py
   ```
3. Hasil pengujian akan menampilkan logs keberhasilan pemblokiran request tanpa CSRF Token dan respons kode HTTP `429` (Too Many Requests) ketika batas rate limit login terlampaui.

---

## ☁️ Panduan Deploy di PythonAnywhere (Free Tier)

Karena PythonAnywhere Free Tier membatasi penggunaan MySQL eksternal dan memiliki kuota penyimpanan (512 MB), disarankan untuk menggunakan konfigurasi hemat penyimpanan berikut:

### 1. Buat Virtual Environment Khusus
Buat virtualenv yang mewarisi pustaka sistem untuk menghemat ruang kuota penyimpanan:
```bash
mkvirtualenv --system-site-packages --python=/usr/bin/python3.10 nusantara-env
```

### 2. Install Dependencies Ringan
Instal pustaka pendukung berukuran kecil tanpa menggunakan cache:
```bash
pip install --no-cache-dir Flask Flask-Login Flask-Migrate Flask-SQLAlchemy Flask-WTF PyMySQL python-dotenv pandas openpyxl
```

### 3. Tarik Kode & Konfigurasi Database SQLite
```bash
cd ~/nusantara-hotel-web
git pull origin main
```
*(File database SQLite Data Warehouse `dw_hospitality.db` sudah terintegrasi di folder `instance/` sehingga aplikasi dapat langsung terhubung).*

### 4. Inisialisasi Database Pengguna (SQLite)
Jalankan perintah ini di Bash Console PythonAnywhere Anda untuk membuat skema tabel pengguna:
```bash
python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. Konfigurasi File WSGI Web App
Di tab **Web** PythonAnywhere Anda, klik tautan **WSGI configuration file** dan ganti seluruh isinya dengan:
```python
import sys
import os

path = '/home/username_anda/nusantara-hotel-web'
if path not in sys.path:
    sys.path.append(path)

from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from app import create_app
application = create_app()
```
*Ganti `username_anda` dengan username PythonAnywhere Anda. Kembali ke tab Web dan klik **Reload**.*

---

## 🔑 Kredensial Akun Default

Gunakan kredensial berikut untuk masuk dan menguji sistem:

| Peran (Role) | Username | Password | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Akses penuh dashboard analitik, kelola user, edit & hapus data DW. |
| **User Biasa** | `user` | `user123` | Akses lihat visualisasi dashboard analitik hotel (read-only). |

---

## 👥 Tim Pengembang (Kelompok 2)

Proyek ini diajukan untuk memenuhi tugas kelompok mata kuliah Data Warehouse & OLAP, program studi Teknik Informatika, **Universitas Musamus Merauke**.

* **Anggota Kelompok**:
  * [Sofyan Baharudin](https://github.com/SofyanBaharudinnn) (Developer Utama)
  * Anggota Kelompok 2 Lainnya
* **Kontak**: hello@nusantarahospitality.com