import os
import re

DICTIONARY = {
    # Nav/Context
    r'>\s*Dashboard\s*<': '>Beranda<',
    r'>\s*Front Desk\s*<': '>Resepsionis<',
    r'>\s*Walk-in Guest\s*<': '>Tamu Langsung<',
    r'>\s*Rooms\s*<': '>Kamar<',
    r'>\s*Guests\s*<': '>Buku Tamu<',
    r'>\s*Reservations\s*<': '>Reservasi<',
    r'>\s*Housekeeping\s*<': '>Tata Graha<',
    r'>\s*Billing\s*<': '>Tagihan<',
    r'>\s*Inventory\s*<': '>Inventaris<',
    r'>\s*POS\s*<': '>Kasir (F&B)<',
    r'>\s*Reports\s*<': '>Laporan<',
    r'>\s*Log Out\s*<': '>Keluar<',
    r'>\s*Profile\s*<': '>Profil<',
    
    # KPIs and Dashboard
    r'>\s*Available Rooms\s*<': '>Kamar Tersedia<',
    r'>\s*Occupied Rooms\s*<': '>Kamar Terisi<',
    r'>\s*Arrivals Today\s*<': '>Check-In Hari Ini<',
    r'>\s*Departures Today\s*<': '>Check-Out Hari Ini<',
    r'>\s*Total Revenue\s*<': '>Total Pendapatan<',
    
    # Common Actions
    r'>\s*Save\s*<': '>Simpan<',
    r'>\s*Cancel\s*<': '>Batal<',
    r'>\s*Delete\s*<': '>Hapus<',
    r'>\s*Edit\s*<': '>Ubah<',
    r'>\s*Search\s*<': '>Cari<',
    r'>\s*Checkout\s*<': '>Check-Out<',
    r'>\s*Checkin\s*<': '>Check-In<',
    r'placeholder="Search': 'placeholder="Cari',
    r'placeholder="Enter': 'placeholder="Masukkan',

    # Table Headers
    r'<th>Room Number</th>': '<th>Nomor Kamar</th>',
    r'<th>Guest</th>': '<th>Nama Tamu</th>',
    r'<th>Status</th>': '<th>Status</th>',
    r'<th>Action</th>': '<th>Aksi</th>',
    r'<th>Date</th>': '<th>Tanggal</th>',
    r'<th>Amount</th>': '<th>Total</th>',
    
    # States
    r'>\s*Available\s*<': '>Tersedia<',
    r'>\s*Occupied\s*<': '>Terisi<',
    r'>\s*Dirty\s*<': '>Kotor<',
    r'>\s*Maintenance\s*<': '>Perbaikan<',

    # Form Titles
    r'>\s*Add New Room\s*<': '>Tambah Kamar Baru<',
    r'>\s*Add Guest\s*<': '>Tambah Tamu<',
    r'>\s*New Reservation\s*<': '>Reservasi Baru<',
}

def translate_html():
    target_dir = 'f:\\0xManta\\templates'
    print("Translating templates in", target_dir)
    count = 0
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original = content
                for eng, indo in DICTIONARY.items():
                    # Handle case-insensitive regex sub
                    content = re.sub(eng, indo, content, flags=re.IGNORECASE)
                
                if content != original:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
    print(f"Translated {count} template files successfully!")

if __name__ == "__main__":
    translate_html()
