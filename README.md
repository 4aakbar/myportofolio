Nama : ANDY AULIA AKBAR

NPM : 2506613590

Kelas : PBP C

#### Menjalankan Proyek

```bash
python -m venv env
env\Scripts\activate            # macOS/Linux: source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # akun pemilik portofolio
python manage.py runserver
python manage.py test              # menjalankan unit test
```


### Tugas 5

Pola AJAX dari Tutorial 05 (yang dipakai di Projects) diterapkan ulang ke halaman **Experience**. Hak akses dari Tugas 4 tetap berlaku: semua orang bisa membaca, pengguna login bisa memberi star, dan hanya superuser yang bisa menambah data.

#### Implementasi

- **Star di Experience**: `Experience.starred_by` (`ManyToManyField` ke `User`, migrasi `0006`) dan view `toggle_star_experience`, sama seperti star di Project.
- **Endpoint JSON**: `/api/experience/` disusun manual dengan `JsonResponse`, berisi data pengalaman beserta `star_count` dan `is_starred` milik pengguna yang sedang login. Username pemberi star tidak ikut dikirim.
- **Halaman kerangka**: `show_experience` tidak lagi mengirim data. `experience.html` mengambil data lewat `fetch()` dan menampilkan kondisi loading, kosong, dan error.
- **Pencarian**: berdasarkan judul, dengan debounce 300 ms. Request lama dibatalkan dengan `AbortController` supaya hasil yang telat datang tidak menimpa hasil terbaru.
- **Tambah lewat modal**: `components/experience_form_modal.html` hanya dirender untuk superuser. Form dikirim ke `create_experience_ajax` dengan `FormData` dan header `X-CSRFToken`. View tersebut mengecek peran di server (403), memvalidasi dengan `ExperienceForm` (201 atau 400 beserta pesan error), lalu daftar dimuat ulang tanpa reload halaman.
- **Toast**: `showToast` menampilkan pesan sukses, pesan validasi dari server (dengan nama field), atau error koneksi.
- **XSS**: `escapeHtml` dipindah ke `static/js/utils.js` (bersama `getCookie`) dan dipakai untuk setiap teks yang disisipkan ke HTML. Di server, `clean_title` dan `clean_description` pada `ExperienceForm` memakai `strip_tags`; judul yang isinya hanya tag HTML ditolak. Form juga menolak tanggal berakhir yang lebih awal dari tanggal mulai.

#### Verifikasi

- `python manage.py test`: 18 test lolos. Test lama yang masih mencari data di HTML diubah agar mengecek endpoint JSON, dan ada test baru untuk endpoint tambah (403 untuk non-superuser, 201, 400, `strip_tags`) serta toggle star.
- Endpoint tambah diuji dengan CSRF aktif: tanpa token 403, GET 405, pengunjung/pengguna biasa/Editor 403.
- `<img src="x" onerror="alert('XSS!')">` sebagai judul ditolak server (400). Jika muncul di deskripsi, tag-nya dibuang sehingga tidak ada alert yang muncul.

#### Pertanyaan Reflektif

1. **Debouncing** adalah teknik menunda eksekusi sebuah fungsi sampai event berhenti terjadi selama jeda tertentu. Pada pencarian, setiap ketikan mereset timer, dan request baru dikirim setelah pengguna berhenti mengetik (di proyek ini 300 ms). Tanpa debouncing, mengetik "magang" akan mengirim 6 request, padahal yang dibutuhkan hanya hasil untuk kata terakhir. Ini membebani server dan jaringan, serta bisa menyebabkan hasil lama yang datang terlambat menimpa hasil terbaru. Debouncing mengurangi jumlah request dan membuat tampilan lebih stabil.

2. `fetch()` bersifat asinkron dan langsung mengembalikan **Promise**, bukan data. `await` menghentikan sementara jalannya fungsi `async` sampai Promise tersebut selesai, lalu memberikan hasilnya (objek `Response`, lalu data JSON dari `response.json()`), sehingga kode bisa ditulis berurutan seperti kode biasa. Error dari Promise yang ditolak juga bisa ditangkap dengan `try...catch`. Tanpa `await`, variabel hanya berisi Promise yang belum selesai, sehingga `response.ok` bernilai `undefined` dan `data.length` akan error atau salah. Kode setelahnya juga langsung jalan sebelum data tiba (misalnya menampilkan "data kosong" padahal data masih dimuat).

3. **XSS (Cross-Site Scripting)** adalah serangan dengan cara menyisipkan script berbahaya ke dalam data, misalnya `<img src="x" onerror="alert('XSS!')">`, sehingga script tersebut dijalankan di browser pengguna lain ketika data ditampilkan. Akibatnya bisa berupa pencurian cookie/sesi, aksi atas nama korban, atau perubahan isi halaman. Template Django melakukan **auto-escaping**: `{{ experience.title }}` otomatis mengubah `<` menjadi `&lt;`, dan seterusnya. Data yang ditampilkan lewat JavaScript tidak melewati template engine. Jika nilai dari JSON dimasukkan dengan `innerHTML`, browser akan memprosesnya sebagai HTML sungguhan, sehingga perlindungan otomatis itu hilang dan escaping harus dilakukan sendiri (`escapeHtml` atau `textContent`). Karena itu, proyek ini juga membersihkan input di server dengan `strip_tags` sebagai lapisan pertahanan kedua.

### AI Disclosure Tugas 5

- **Tools**: Claude
- **Strategi prompting**: soal saya berikan ke AI, lalu saya minta AI membandingkan isi soal dengan kode yang sudah ada dan membagi pekerjaan menjadi 5 tahap. AI mengajarkan dan memberi tahu apa yang harus saya lakukan. lalu saya kerjakan dan saya cek ulang di AI apakah sudah benar.

- **Bagian yang dibantu AI**: field star dan endpoint JSON Experience, `static/js/utils.js`, script AJAX di `experience.html` (render, pencarian dengan debounce, tambah lewat modal, toast), view `create_experience_ajax`, `strip_tags` dan validasi tanggal di `ExperienceForm`, update unit test, dan dokumentasi ini.
- **Prompt**:
  - "gw mau jadi 5 tahap, kira-kira apa aja?"
  - "gw mau lu jelasin tiap tahap secara rinci ke gw biar gw ngerti cara ngerjainnya dan bisa ngerjain sendiri"

- **Keterbatasan AI yang terlihat**:
  - AI tidak bisa membuka halaman soal karena situs memakai proteksi anti-bot, jadi isi soal harus saya copy-paste.

