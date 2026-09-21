Nama : ANDY AULIA AKBAR

NPM : 2506613590

Kelas : PBP C


### Tugas 3

1. Saya pakai ModelForm (ProjectForm dan ExperienceForm) karena field, tipe input, dan validasinya otomatis diturunkan dari model, jadi tidak perlu menulis ulang tiap field dan validasinya secara manual, dan form.save() sudah tahu cara menyimpan ke model terkait. csrf_token wajib ada di setiap form supaya Django bisa memverifikasi request POST benar-benar berasal dari form aplikasi ini, bukan dari situs lain yang mencoba mengirim request atas nama pengguna (serangan CSRF); tanpa token ini request POST akan ditolak.

2. JSON lebih disukai karena strukturnya lebih ringkas dari XML (tanpa closing tag), sehingga lebih kecil dan lebih cepat diparsing, serta native dipetakan ke object/array JavaScript sehingga langsung bisa dipakai di front-end tanpa parsing tambahan. Django juga sudah menyediakan serializers.serialize untuk JSON, jadi implementasinya jauh lebih sederhana dibanding membangun struktur XML manual. XML masih unggul untuk validasi struktur ketat lewat XML Schema, tapi untuk API sederhana seperti di proyek ini JSON lebih efisien.

3. Alurnya: request GET masuk ke view seperti get_projects_json, lalu data diambil dari database lewat ORM (mis. Project.objects.all()), hasilnya berupa objek model Python yang belum bisa langsung jadi teks JSON. Objek ini perlu diserialize (serializers.serialize) supaya diubah jadi representasi JSON standar berisi field dan value dalam tipe data primitif. Proses ini perlu karena objek model punya tipe data yang tidak otomatis bisa diubah ke teks (mis. UUID atau DateTime), sehingga tanpa serialization datanya tidak konsisten atau gagal diproses. Hasilnya dibungkus HttpResponse dengan content_type JSON lalu dikirim ke client, sehingga bisa dibaca klien apa pun tanpa perlu tahu struktur model Django-nya.

### AI Disclosure Tugas 3

Saya menggunakan AI untuk membantu memahami ModelForm, csrf_token, JSON vs XML, dan alur serialization di atas sebelum menulis jawaban dengan pemahaman dan verifikasi personal. Saya juga berdiskusi dengan AI soal penyamaan pola show_experience dengan show_projects, penambahan fitur pencarian di halaman experience, kemampuan update pada Project, serta input tanggal mulai pada Experience beserta tampilan rentang tanggalnya. Hasilnya saya verifikasi lewat manage.py check, migrate, dan runserver sebelum saya commit dan push sendiri.


