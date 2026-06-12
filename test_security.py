import urllib.request
import urllib.parse
import urllib.error
import re
from http.cookiejar import CookieJar

BASE_URL = "http://127.0.0.1:5000"

def test_csrf_protection_without_token():
    print("\n=== Menguji Proteksi CSRF (POST /login Tanpa Token) ===")
    data = urllib.parse.urlencode({
        'username': 'admin',
        'password': 'incorrect_password'
    }).encode()
    try:
        req = urllib.request.Request(f"{BASE_URL}/login", data=data, method='POST')
        response = urllib.request.urlopen(req)
        print(f"POST Status: {response.getcode()} (Lolos - Proteksi CSRF Tidak Aktif!)")
    except urllib.error.HTTPError as e:
        print(f"POST Status: {e.code} ({e.reason if hasattr(e, 'reason') else 'Terblokir CSRF - Sukses'})")
    print("-" * 50)

def test_csrf_protection_with_token():
    print("\n=== Menguji Proteksi CSRF (POST /login Dengan Token Valid) ===")
    
    # Gunakan CookieJar untuk mengelola session cookie
    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    
    # 1. Lakukan GET request untuk mengambil halaman login dan CSRF token
    try:
        response = opener.open(f"{BASE_URL}/login")
        html_content = response.read().decode('utf-8')
        
        # Cari input hidden csrf_token
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html_content)
        if not match:
            match = re.search(r'value="([^"]+)"\s+name="csrf_token"', html_content)
            
        if match:
            csrf_token = match.group(1)
            print(f"Ditemukan CSRF Token: {csrf_token[:15]}...")
            
            # 2. Kirim POST request dengan CSRF token dan cookie session yang sama
            post_data = urllib.parse.urlencode({
                'csrf_token': csrf_token,
                'username': 'admin',
                'password': 'incorrect_password'
            }).encode()
            
            try:
                post_response = opener.open(f"{BASE_URL}/login", data=post_data)
                print(f"POST Status: {post_response.getcode()} (Sukses melewati CSRF Protect)")
            except urllib.error.HTTPError as e:
                print(f"POST Status: {e.code} ({e.reason})")
        else:
            print("Gagal menemukan CSRF token di halaman login.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
    print("-" * 50)

def test_rate_limiting_get():
    print("\n=== Menguji Rate Limiting (GET /login) ===")
    print("Batas rate limit: 5 kali per menit. Kita akan mencoba 7 kali.")
    for i in range(1, 8):
        try:
            req = urllib.request.Request(f"{BASE_URL}/login")
            req.add_header('Cache-Control', 'no-cache')
            response = urllib.request.urlopen(req)
            print(f"Percobaan GET {i}: Status {response.getcode()} (Sukses)")
        except urllib.error.HTTPError as e:
            # Jika limit terlampaui, harusnya mengembalikan HTTP 429
            print(f"Percobaan GET {i}: Status {e.code} (Terblokir Rate Limiter - Sukses)")
    print("-" * 50)

if __name__ == "__main__":
    print("Memulai Pengujian Keamanan Nusantara Hotel Web")
    print("Pastikan server lokal Flask sudah aktif di http://127.0.0.1:5000\n")
    
    # 1. Uji CSRF terlebih dahulu sebelum rate limit GET /login tercapai
    test_csrf_protection_without_token()
    test_csrf_protection_with_token()
    
    # 2. Uji Rate Limiting
    test_rate_limiting_get()
