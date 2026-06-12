# Nusantara Hospitality Group - Data Analytics & Warehouse Portal

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.1-red.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20MySQL-lightgrey.svg)](https://www.sqlite.org/)

Platform Intelijen Bisnis (BI) terpadu untuk memonitor, menganalisis, dan memaksimalkan potensi operasional hotel, resor, dan properti di bawah naungan **Nusantara Hospitality Group**. Sistem ini menghubungkan database Data Warehouse transaksional dengan antarmuka visual modern berbasis web.

Proyek ini dikembangkan oleh **Kelompok 2** sebagai tugas akhir mata kuliah **Data Warehouse & OLAP** di **Universitas Musamus Merauke**.

---

## 🌟 Fitur Utama

### 1. Visualisasi Peta 3D Indonesia (Landing Page)
* Render interaktif peta kepulauan Indonesia secara 3D menggunakan **Three.js** dan WebGL.
* Garis tepi pulau (*neon glowing outlines*) Sumatera, Jawa, Kalimantan, Sulawesi, Papua, dan Nusa Tenggara.
* Pin operasional 3D dengan label nama kota (billboard text) pada hub utama: **Medan, Jakarta, Surabaya, Makassar, dan Jayapura**.
* Efek aliran data dinamis (*arc curves*) dengan partikel bergerak berwarna emas yang menghubungkan antar hub utama.

### 2. Dashboard Analitik & Visualisasi (Admin & User)
* **Indikator Kunci (KPIs)**: Total Reservasi, Total Pendapatan (*Revenue*), Rata-rata Durasi Inap (*Avg Nights*), Jumlah Tamu Unik, dan Persentase Pembatalan (*Cancel Rate*).
* **Tren Pendapatan & Okupansi**: Grafik kuartalan tren hunian per tipe hotel (City Hotel vs Resort Hotel).
* **Distribusi Booking Channel**: Diagram lingkaran alur pemesanan (Direct, OTA, Agent).
* **Segmentasi Tamu**: Analisis tipe segmen pasar (Corporate, Aviation, Online TA, Groups, dsb).
* **Statistik Lainnya**: Tren musiman pendapatan, tipe kamar terlaris, asal negara tamu teratas, serta data reservasi terbaru.

### 3. Ekspor Laporan (Data Export)
* Pengunduhan laporan data reservasi, okupansi, kamar, dan customer secara langsung ke format **Excel (.xlsx)** atau **CSV (.csv)** yang terintegrasi dengan pustaka `pandas` dan `openpyxl`.

### 4. Manajemen Pengguna (User CRUD)
* Dashboard kontrol untuk Administrator guna menambah, mengedit (role, username, email, password), dan menghapus pengguna sistem analitik.

### 5. Pengelolaan Data Warehouse (Data CRUD)
* Fitur manipulasi data langsung pada tabel fakta dan dimensi Data Warehouse untuk:
  - **Tamu / Customers** (`dim_guest`)
  - **Kamar / Rooms** (`dim_room`)
  - **Properti Hotel & Okupansi** (`dim_hotel`)
* Pembaruan (*Update*) dan Penghapusan (*Delete*) data yang terhubung langsung ke mesin relasional database.

### 6. Sistem Autentikasi & Registrasi Mandiri
* Pembatasan hak akses berbasis peran (Admin & User).
* *Toggle* transisi mulus (*client-side*) antara form login dan form registrasi akun baru.
* Layar tunggu transisi (*loading spinner overlay*) dengan animasi dinamis selama proses validasi akun.

---

## 🛠️ Tech Stack

* **Backend**: Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
* **Database**: SQLite (Bawaan & Direkomendasikan untuk free hosting) / MySQL (Enterprise DW)
* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & Neon Dark Theme), JavaScript (ES6)
* **Libraries**: Three.js (3D Map), Chart.js (Interactive Charts), Pandas & OpenPyXL (Excel Generator), PyMySQL (MySQL Driver)

---

## 💻 Panduan Instalasi Lokal

### 1. Prasyarat
Pastikan komputer Anda sudah terinstal:
* [Python 3.10 atau versi terbaru](https://www.python.org/downloads/)
* Database MySQL (misal menggunakan XAMPP atau Laragon) jika ingin menggunakan MySQL.

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
Buat file bernama `.env` di direktori utama proyek, lalu isi dengan konfigurasi berikut:
```ini
SECRET_KEY=nusantara-super-secret-key-2024
DATABASE_URL=sqlite:///users.db
DW_DATABASE_URL=sqlite:///instance/dw_hospitality.db
FLASK_ENV=development
FLASK_DEBUG=1
```
*(Secara default, aplikasi dikonfigurasi menggunakan SQLite untuk database pengguna dan Data Warehouse agar langsung berjalan).*

### 5. Jalankan Aplikasi
```bash
python run.py
```
Buka browser Anda dan akses: [**`http://127.0.0.1:5000`**](http://127.0.0.1:5000)

---

## ☁️ Panduan Deploy di PythonAnywhere (Free Tier)

Karena PythonAnywhere membatasi MySQL untuk akun gratis dan membatasi penyimpanan kuota (512 MB), ikuti langkah instalasi hemat penyimpanan ini:

### 1. Buat Virtual Environment Khusus
Buat virtualenv yang mewarisi pustaka sistem agar menghemat memori penyimpanan global:
```bash
mkvirtualenv --system-site-packages --python=/usr/bin/python3.10 nusantara-env
```

### 2. Install Dependencies Ringan
Instal library pendukung berukuran kecil tanpa menggunakan cache:
```bash
pip install --no-cache-dir Flask Flask-Login Flask-Migrate Flask-SQLAlchemy Flask-WTF PyMySQL python-dotenv
```

### 3. Tarik Kode & Database Terkonversi dari GitHub
```bash
cd ~/nusantara-hotel-web
git pull origin main
```
*(File database SQLite Data Warehouse `dw_hospitality.db` sudah terintegrasi di folder `instance/` sehingga aplikasi dapat langsung berjalan tanpa MySQL).*

### 4. Inisialisasi Database Pengguna (SQLite)
Jalankan perintah ini di Bash Console PythonAnywhere Anda untuk membuat tabel pengguna:
```bash
python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. Konfigurasi File WSGI Web App
Di tab **Web** PythonAnywhere Anda, klik tautan **WSGI configuration file** dan ganti isinya dengan:
```python
import sys
import os

path = '/home/NusantaraHotelWeb/nusantara-hotel-web'
if path not in sys.path:
    sys.path.append(path)

from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from app import create_app
application = create_app()
```
*Kembali ke tab Web dan klik **Reload**.*

---

## 🔑 Kredensial Akun Default

Gunakan kredensial berikut untuk menguji sistem:

| Peran (Role) | Username | Password | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Akses penuh dashboard, kelola user, edit & hapus data DW. |
| **User Biasa** | `user` | `user123` | Akses lihat visualisasi dashboard analitik hotel. |

---

## 👥 Tim Pengembang (Kelompok 2)

Proyek ini diajukan untuk memenuhi tugas mata kuliah Data Warehouse & OLAP, program studi Teknik Informatika, **Universitas Musamus Merauke**.

* **hello@nusantarahospitality.com**