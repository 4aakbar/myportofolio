Nama : ANDY AULIA AKBAR

NPM : 2506613590

Kelas : PBP C



### Tugas 4

Melanjutkan Tutorial 04 (register, login, logout, cookie `last_login`, dan star pada Project), tugas ini menambahkan otorisasi berbasis peran untuk data Project dan Experience.

#### Implementasi

- **Peran Editor**: grup `Editor` dibuat otomatis oleh migrasi `main/migrations/0005_create_editor_group.py` beserta permission `change_project` dan `change_experience`. Akun dijadikan Editor lewat Django Admin.
- **Pengecekan di server**: aturan peran dikumpulkan di `main/permissions.py` (`is_editor`, `can_update`, `can_create_or_delete`). Setiap view create/update/delete memakai `@login_required` (pengunjung diarahkan ke login) lalu memanggil helper tersebut dan melempar `PermissionDenied` (HTTP 403) jika tidak berhak.
- **Template**: `show_projects` dan `show_experience` mengirim `can_update` dan `can_create_or_delete` ke template, sehingga tombol Tambah/Edit/Hapus hanya tampil bagi peran yang berhak. Template tidak mengecek `is_superuser` sendiri, jadi aturan peran hanya ada di satu tempat.
- **Star**: `Project.starred_by` adalah `ManyToManyField` ke `User`. View `toggle_star` hanya memproses POST dengan `{% csrf_token %}` dan memakai `add`/`remove`, sehingga satu pengguna maksimal memberi satu star. Kartu proyek menampilkan jumlah star dan status Star/Unstar milik pengguna.
- **Endpoint JSON**: `/api/projects/` sebelumnya ikut mengirim `starred_by` berisi username semua pemberi star kepada siapa pun. Sekarang field yang diserialisasi dibatasi eksplisit, jadi data akun pengguna tidak ikut terkirim. `/api/experience/` tidak memiliki relasi ke `User`.


#### Verifikasi

Semua peran diuji dengan Django test client di database uji sementara (data asli tidak tersentuh): setiap endpoint create/update/delete/star dicoba sebagai pengunjung, pengguna biasa, Editor, dan superuser, lalu status responsnya (302 ke login / 403 / 200) dan tombol yang tampil di template dicocokkan dengan tabel di atas. `python manage.py check` tidak menemukan masalah.

### AI Disclosure Tugas 4

- Tools: Claude
- **Strategi prompting**: saya meminta AI membaca soal lalu memecahnya menjadi tahapan tanpa langsung mengerjakan. Setiap tahap saya review, lalu saya commit sendiri sebelum lanjut ke tahap berikutnya
- **Bagian yang dibantu AI**: `main/permissions.py`, migrasi grup Editor, pengecekan peran di view Project dan Experience, penyesuaian template, pembatasan field pada `/api/projects/`, dan dokumentasi ini
- **prompt**: coba lihat tugas ini, coba ubah tugas ini menjadi 4 bagian. tiap bagian dibagi lagi menjadi langkah, langkah yang perlu saya kerjakan. saya akan mengerjakan 4 bagian itu secara berkala dan anda harus mengecek apakah langkah sudah sesuai atau belum dan jelaskan bagaimana semua di bagian itu bekerja
- **Keterbatasan AI yang terlihat**: tidak ada sejauh ini.

