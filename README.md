📦 MD5 Tools

MD5 Tools adalah aplikasi Python yang dapat dijalankan sebagai web/desktop serta dapat dibangun menjadi aplikasi Android menggunakan Briafcase.

🚀 Persiapan Lingkungan

Pastikan sudah terinstall:

Python 3.x

pip

virtualenv (opsional tapi disarankan)

Briafcase

🛠️ Setup Project
1️⃣ Buat Virtual Environment
python -m venv .env


Aktifkan virtual environment:

Windows

.env\Scripts\activate


Linux / macOS

source .env/bin/activate

2️⃣ Install Dependency
python -m pip install -r requirements.txt

▶️ Menjalankan Aplikasi (Web / Desktop)
python pythonfile.py


Pastikan nama file Python utama sesuai (pythonfile.py).

📱 Build Aplikasi Android
1️⃣ Masuk ke Folder Project
cd md5tools

2️⃣ Test Mode Development
briafcase dev

3️⃣ Create Project Android
briafcase create android

4️⃣ Build Android
briafcase build android

5️⃣ Jalankan di Perangkat / Emulator
briafcase run android
