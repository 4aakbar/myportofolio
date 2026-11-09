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
python manage.py test main         # menjalankan unit test (tanpa test_e2e Selenium)
```

Browsable API dapat dibuka di `http://localhost:8000/api/v1/projects/` dan `http://localhost:8000/api/v1/experience/`.


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

### Tugas 6

Pola Django REST Framework dari Tutorial 07 diterapkan ke bagian **Experience**. Hak akses empat peran dari Tugas 4 tetap berlaku di API:

| Peran | Baca daftar/detail | Star | PUT/PATCH | POST/DELETE |
|---|---|---|---|---|
| Pengunjung tanpa login | ✅ | ❌ | ❌ | ❌ |
| Pengguna biasa | ✅ | ✅ | ❌ | ❌ |
| Editor | ✅ | ✅ | ✅ | ❌ |
| Pemilik (superuser) | ✅ | ✅ | ✅ | ✅ |

#### Endpoint

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/api/v1/experience/?title=...` | Daftar experience, pencarian berdasarkan judul |
| POST | `/api/v1/experience/` | Tambah experience (201) |
| GET | `/api/v1/experience/<uuid>/` | Detail experience |
| PUT / PATCH | `/api/v1/experience/<uuid>/` | Ubah experience |
| DELETE | `/api/v1/experience/<uuid>/` | Hapus experience (204) |
| POST | `/api/v1/experience/<uuid>/star/` | Beri atau batalkan star |

#### Implementasi

- **Penyesuaian Tutorial 07**: API Projects ditulis ulang menjadi function view `@api_view` di `main/api_urls.py` dengan prefix `/api/v1/`. Projects sekarang hanya dikelola pemilik (`IsPortfolioOwnerOrReadOnly`), sedangkan peran Editor berlaku di Experience.
- **Serializer**: `ExperienceSerializer` di `main/serializers.py` memakai daftar `fields` eksplisit. `star_count`, `is_starred`, `is_ongoing`, dan `category_display` bersifat read-only, dan `starred_by` tidak dikirim sehingga data akun pemberi star tidak terekspos. `validate_title` dan `validate_description` memakai `strip_tags` seperti `clean_<field>` di `ExperienceForm`, dan `validate()` menolak tanggal berakhir yang lebih awal dari tanggal mulai. Saat PATCH, tanggal yang tidak dikirim diambil dari data yang tersimpan.
- **Permission**: `IsPortfolioOwnerOrEditorOrReadOnly` di `main/permissions.py` dipasang pada endpoint daftar dan detail. Endpoint star memakai `IsAuthenticated`, dan akun pemberi star selalu diambil dari `request.user`.
- **API view**: `experience_list`, `experience_detail`, dan `experience_star` di `main/api_views.py` memakai `@api_view` dan `SessionAuthentication`. Status yang dikembalikan: 201 saat dibuat, 400 untuk input tidak valid, 403 untuk tindakan yang tidak diizinkan, 404 untuk data yang tidak ada, dan 204 setelah dihapus.
- **Integrasi halaman**: `experience.html` menampilkan, mencari, menambah, memberi star, dan menghapus data lewat API tanpa reload. Semua request yang mengubah data lewat satu helper `sendApiRequest` yang mengirim JSON dan header `X-CSRFToken`. Error 400 dan 403 dari API ditampilkan lewat toast beserta nama field-nya, dan setiap teks tetap di-escape dengan `escapeHtml`.
- **Modal edit**: `components/experience_edit_modal.html` hanya dirender untuk Editor dan pemilik. Modal diisi dari data hasil fetch terakhir, lalu dikirim sebagai PATCH ke API.
- **Pembersihan**: `get_experience_json`, `create_experience_ajax`, dan `toggle_star_experience` dihapus karena sudah digantikan API. Halaman tambah/edit/hapus dari Tugas 3 tetap ada dan hak aksesnya sama dengan API.

#### Verifikasi

- `python manage.py test main`: 47 test lolos, termasuk test dari Tutorial 07.
- `ExperienceAPITest` (20 test) mencakup setiap peran dan memeriksa isi database pada test penolakan, validasi input, star (termasuk penolakan pengunjung dan akun yang selalu diambil dari `request.user`), serta CSRF dengan `APIClient(enforce_csrf_checks=True)` dan `.login()`.
- `ExperienceViewPermissionTest` memastikan halaman lama dari Tugas 3 mengikuti aturan peran yang sama.
- Untuk memastikan test permission benar-benar bekerja, permission sementara diubah agar semua akun login boleh menulis. Test hak akses langsung gagal, lalu permission dikembalikan.

#### Pertanyaan Reflektif

1. **REST** (*Representational State Transfer*) adalah gaya arsitektur untuk merancang web API, bukan library atau format data. Data diperlakukan sebagai *resource* yang ditunjuk oleh URL (`/api/v1/experience/` untuk kumpulan, `/api/v1/experience/<uuid>/` untuk satu data), HTTP method menyatakan tindakannya (GET membaca, POST membuat, PUT/PATCH mengubah, DELETE menghapus), klien dan server bertukar representasi data, dan setiap request membawa informasi yang dibutuhkan (stateless). Karena itu, mengembalikan JSON saja belum cukup. Endpoint seperti `POST /experience/add-ajax/` atau `POST /experience/<id>/delete/` juga bisa mengembalikan JSON, tetapi tindakannya ditulis di URL dan method-nya tidak mencerminkan aksi yang dilakukan. Status code yang dipakai juga harus tepat, misalnya 201 untuk data baru dan 404 untuk data yang tidak ada.

   **PUT** mengganti seluruh representasi resource, jadi semua field wajib harus dikirim. **PATCH** hanya mengubah field yang dikirim, dan field lain tetap memakai nilai lama. PUT cocok untuk form edit yang selalu mengirim semua field. PATCH cocok untuk perubahan sebagian, misalnya hanya mengisi tanggal berakhir ketika sebuah pengalaman selesai. Di proyek ini `PATCH {"ended_at": "2026-06-30"}` berhasil, sedangkan `PUT` dengan data tidak lengkap ditolak dengan 400.

2. **Serializer** pada DRF bekerja dua arah. Saat membaca (*serialization*), serializer mengubah objek model menjadi tipe data Python yang bisa dirender menjadi JSON. Saat menerima input (*deserialization*), serializer memvalidasi data dari klien lalu menyimpannya lewat `.save()`. Dibandingkan merakit dictionary manual dengan `JsonResponse` seperti di Tutorial 05, serializer memberikan satu kontrak data yang dipakai untuk membaca sekaligus menulis, validasi per field (`validate_<field>`) dan lintas field (`validate()`) dengan pesan error otomatis berstatus 400, field read-only yang tidak bisa diisi klien, dan implementasi `create`/`update` dari `ModelSerializer`. Hasilnya, kode lebih pendek dan tidak berulang untuk setiap endpoint. Kalau ada field baru, perubahannya cukup di satu tempat, tidak di banyak loop dictionary.

3. **Autentikasi** menjawab *siapa pengirim request*. Di DRF, authentication class seperti `SessionAuthentication` membaca session lalu mengisi `request.user`. **Otorisasi** menjawab *apa yang boleh dilakukan pengguna tersebut*, dan diputuskan oleh permission class seperti `IsPortfolioOwnerOrEditorOrReadOnly` sebelum isi view dijalankan. Hak akses harus diperiksa di server karena menyembunyikan tombol di template hanya mengubah tampilan. Siapa pun tetap bisa mengirim request langsung ke endpoint lewat DevTools, `curl`, atau Browsable API, tanpa pernah menyentuh tombol tersebut. Satu-satunya tempat yang tidak bisa diubah oleh klien adalah server, jadi permission class menjadi batas keamanan yang sesungguhnya. Menyembunyikan tombol hanya untuk kenyamanan pengguna.

4. Dengan `SessionAuthentication`, browser **otomatis** mengirim cookie session ke domain kita, termasuk ketika request dipicu oleh situs lain. Tanpa token CSRF, situs jahat bisa membuat form atau script yang mengirim `POST`/`DELETE` ke API kita, dan request itu akan dianggap berasal dari pengguna yang sedang login (*Cross-Site Request Forgery*). Token CSRF adalah nilai rahasia yang hanya bisa dibaca oleh halaman dari origin kita dan harus dikirim lewat header `X-CSRFToken`, sehingga request dari situs lain bisa ditolak. Karena itu DRF selalu memeriksa token CSRF untuk request yang mengubah data dari pengguna yang login lewat session. `force_authenticate` tidak cukup untuk membuktikan perlindungan ini, karena method tersebut langsung menetapkan `request.user` dan melewati proses autentikasi session, termasuk pemeriksaan CSRF. Test dengan `force_authenticate` tetap lolos walaupun token tidak dikirim. Untuk membuktikan CSRF benar-benar diperiksa, test harus memakai `APIClient(enforce_csrf_checks=True)` dan `.login()` agar terbentuk session sungguhan, lalu memastikan request tanpa token ditolak dengan 403.

### AI Disclosure Tugas 6

- **Tools**: Claude Code (di VS Code)
- **Strategi prompting**: Saya mengerjakan Tugas 6 dengan sedikit panduan AI, lalu saya mengeceknya dengan memberikan halaman tugas ke AI untuk pengecekan.
- **Bagian yang dibantu AI**: pengecekan dan refactor API Projects agar sesuai Tutorial 07, `ExperienceSerializer`, permission class, API view dan URL Experience, script API dan modal edit di `experience.html`, penghapusan endpoint lama, test di `tests_api.py` dan `tests.py`, serta dokumentasi ini.