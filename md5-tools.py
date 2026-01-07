import hashlib
import requests
import sys
from time import sleep

def cheap_md5_lookup(hash_value: str) -> str | None:
    hash_value = hash_value.strip().lower()
    if len(hash_value) != 32:
        return "Not a valid MD5 hash (must be 32 hex chars)"

    sites = [
        f"http://www.nitrxgen.net/md5db/{hash_value}.txt",
        f"https://md5.gromweb.com/?md5={hash_value}",
        # Many others are dead or blocked Cloudflare in 2025-2026
    ]

    for url in sites:
        try:
            r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
            sleep(1.2) 

            if not r.text or ("Not found" in r.text or "No match" in r.text or "could not" in r.text.lower()):
                continue

            if "gromweb" in url:
                if "/?string=" in r.text.lower():
                    start = r.text.find('The MD5 hash') + 100
                    end = r.text.find("</p>", start)
                    string = r.text[start:end].strip().strip('"').strip("'")
                    parse = string.split('/?string=')[-1].split('"')[0].strip()
                    return parse.replace("%20", " ")
            if "nitrxgen" in url and ".txt" in url:
                return r.text 
            else:
                import re
                candidates = re.findall(r'>[^<]{3,40}</', r.text)
                for cand in candidates:
                    plain = cand[1:-2].strip()
                    if hashlib.md5(plain.encode()).hexdigest() == hash_value:
                        return plain

        except Exception:
            continue

    return None

def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def main():
    while True:
        print("\n" + "═" * 45)
        print("           MD5 TOOL - MENU")
        print("═" * 45)
        print("  1. Hash string menjadi MD5")
        print("  2. Coba kembalikan MD5 ke plaintext (reverse lookup)")
        print("  q. Keluar")
        print("═" * 45)

        choice = input("\nPilih menu (1/2/q): ").strip().lower()

        if choice in ('q', 'quit', 'exit'):
            print("\nTerima kasih telah menggunakan tool ini. Selamat tinggal! 👋\n")
            sys.exit(0)

        elif choice == '1':
            text = input("Masukkan string yang akan di-hash: ").strip()
            if not text:
                print("String kosong tidak diizinkan!\n")
                continue
            result = md5_hash(text)
            print(f"\nMD5({text}) = \033[92m{result}\033[0m\n")

        elif choice == '2':
            h = input("Masukkan MD5 hash (32 hex chars): ").strip()
            print("Mencari... (bisa butuh beberapa detik)", end="", flush=True)
            
            result = cheap_md5_lookup(h)
            
            print("\r" + " " * 60 + "\r", end="", flush=True)
            
            if result:
                print(f"Plaintext ditemukan : \033[92m{result}\033[0m")
                print(f"MD5({result}) = {h}\n")
            else:
                print("Maaf, tidak ditemukan di layanan lookup publik yang tersedia...")
                print("(Banyak situs sudah mati atau diblokir di 2026)\n")
                print("Coba gunakan Hashcat + wordlist bagus untuk hasil lebih baik.\n")

        else:
            print("Pilihan tidak valid! Masukkan 1, 2 atau q\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDihentikan oleh pengguna. Sampai jumpa! 👋\n")
        sys.exit(0)