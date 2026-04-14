# MantaHotel - Panduan & Dokumentasi Resmi

MantaHotel adalah sistem manajemen properti hotel (*Property Management System* / PMS) modern berbasis Website / Cloud yang dirancang khusus untuk operasional perhotelan di Indonesia.

## 🚀 Teknologi Utama
- **Backend:** Python + Django 5
- **Frontend Dinamis:** HTMX + Alpine.js
- **Database:** PostgreSQL (Supabase Serverless)
- **Desain UI:** DaisyUI & Tailwind CSS

Sistem ini bersifat ringan, cepat, dan bekerja layaknya aplikasi *Native* (Single-Page Application) berkat implementasi HTMX yang meminimalisir *loading* halaman secara penuh.

## 💼 Modul / Fitur Sistem
- **Dashboard Eksekutif**: Tinjauan metrik hotel, pendapatan, tingkat okupansi secara *real-time*.
- **Resepsionis & Reservasi**: Penanganan Kedatangan (*Check-in*), Keberangkatan (*Check-out*), dan *Walk-in Guest*.
- **Manajemen Kamar**: Penentuan harga dinamis, tipe kamar, dan status visual (*Tersedia, Terisi, Kotor*).
- **Tata Graha (Housekeeping)**: Manajemen perputaran status kebersihan kamar.
- **Kasir F&B (Restoran)**: Modul *Point of Sales* terintegrasi. Tamu dapat membebankan pesanan Restoran langsung ke Tagihan Kamar (*Folio*).
- **Tagihan (Billing/Folio)**: Rekapitulasi otomatis biaya kamar, F&B, dan Pajak+Layanan.

## 🛠 Instalasi & Menjalankan Lokal

1. **Kloning Repositori:**
   ```bash
   git clone https://github.com/awangsuryarmdhn/hotelku.git
   cd hotelku
   ```

2. **Pengaturan Virtual Environment & Dependencies:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Untuk pengguna Windows
   pip install -r requirements.txt
   ```

3. **Konfigurasi Lingkungan (`.env`):**
   Salin `.env.example` menjadi `.env` dan masukkan konfigurasi Supabase Database Anda.

4. **Injeksi Data Skema Demo (Sekali Jalan):**
   Jalankan perintah lokal ini untuk menyiapkan SuperAdmin (`admin` / `manta2026`) beserta data dummy Bahasa Indonesia siap pakai.
   ```bash
   python manage.py migrate
   python manage.py seed_demo
   ```

5. **Jalankan Aplikasi:**
   ```bash
   python manage.py runserver
   ```
   Buka `http://127.0.0.1:8000` di peramban Anda.

## 🌐 Mode Produksi Vercel
Aplikasi ini sudah diprogram agar selaras dengan ekosistem Serverless Vercel menggunakan file integrasi `build_files.sh` dan `vercel.json`.

Jika karena alasan tertentu database kosong di produksi, cukup kunjungi tautan Rahasia:
`https://<domain-vercel-anda>.vercel.app/setup-db/` 
Sistem akan otomatis melakukan Migrasi, membuat akun Admin, dan meng-*inject* seluruh data presentasi Demo dalam 1 klik!
