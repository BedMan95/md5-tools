# MD5 Tools python

## Setup

### Membuat virtual environment
```bash
python -m venv .env
```

### Mengaktifkan virtual environment

**Windows:**
```bash
.env\Scripts\activate
```

**Unix/macOS:**
```bash
source .env/bin/activate
```

### Menginstal dependensi
```bash
python -m pip install -r requirements.txt
```

## 💻 Menjalankan Aplikasi

### Web & Desktop
Untuk menjalankan aplikasi dalam mode pengembangan (development) di desktop atau web, gunakan perintah berikut:

```bash
python pythonfile.py
```

## 📱 Build untuk Android

Proyek ini menggunakan BeeWare/Briefcase untuk mengemas aplikasi ke perangkat Android.

### 1. Masuk ke Direktori Tools
```bash
cd md5tools
```

### 2. Mode Pengembangan (Dev)
Gunakan perintah ini untuk mencoba aplikasi secara cepat tanpa melakukan build penuh:

```bash
briefcase dev
```

### 3. Build & Run di Android
Ikuti urutan ini untuk membuat paket aplikasi dan menjalankannya di emulator atau perangkat fisik:

```bash
# Membuat struktur proyek Android
briefcase create android

# Mengompilasi aplikasi
briefcase build android

# Menjalankan aplikasi di perangkat/emulator
briefcase run android
```
