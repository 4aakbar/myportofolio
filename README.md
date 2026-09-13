Nama : ANDY AULIA AKBAR

NPM : 2506613590

Kelas : PBP C

### Tugas 1

1. Dalam membuat struktur HTML, saya menggunakan beberapa elemen semantik HTML5 seperti `<section>`, `<article>`, dan `<header>`. Penggunaan elemen tersebut membantu saya membagi halaman berdasarkan tujuan dan jenis kontennya, misalnya bagian About Me, Skills, dan Projects. Selain membuat struktur kode lebih mudah dibaca, elemen semantik juga membuat hubungan antarbagian halaman menjadi lebih jelas. Dengan begitu, saya tidak hanya mengandalkan `<div>` untuk semua bagian halaman dan lebih mudah melakukan pengembangan ketika website ini nantinya menjadi lebih kompleks.

2. Tantangan utama ketika membuat website responsive adalah menyesuaikan ukuran dan posisi beberapa elemen agar tetap nyaman dilihat pada layar, layar desktop maupun layar mobile. Layout yang terlihat seimbang di desktop tidak selalu cocok ketika dipindahkan ke mobile, terutama pada bagian yang menggunakan beberapa kolom. Bahkan layout yang sekarang saat saya lihat di mobile masih ada blank space di bagian kanannya.

3. Karena website ini masih berupa static web, informasi di dalamnya harus ditulis langsung pada HTML sehingga kurang fleksibel ketika ingin menambahkan atau memperbarui data. Saya juga belum dapat membuat fitur yang benar-benar berinteraksi dengan pengguna atau menyimpan data secara dinamis. Pada iterasi berikutnya, saya paling ingin menambahkan fungsionalitas dinamis pada bagian Projects, misalnya mengambil data proyek dari sumber external sehingga proyek baru dapat ditambahkan tanpa harus mengubah struktur HTML secara manual.

### AI Disclosure Tugas 1

Dalam pengerjaan Tugas 1, saya menggunakan AI sebagai alat bantu untuk memahami dan mengevaluasi implementasi HTML dan CSS. AI digunakan terutama untuk memberikan saran mengenai struktur HTML semantik, responsive layout, perbaikan CSS, serta saran untuk layout dan tema. Saya tetap melakukan implementasi dan penyesuaian kode secara mandiri, termasuk menyesuaikan desain dengan kebutuhan website portofolio dan menguji hasilnya melalui browser serta `python manage.py runserver`. Saya juga mengevaluasi kembali saran yang diberikan AI dan melakukan perubahan secara manual ketika hasilnya tidak sesuai dengan desain yang saya inginkan.

### Tugas 2

1. Ketika pengguna membuka halaman baru (misalnya `/projects/`), browser mengirim request ke server Django. `portofolio/urls.py` (urls.py tingkat proyek) menerima request tersebut dan langsung mendelegasikannya ke `main/urls.py` lewat `include("main.urls")`, karena semua path pada proyek ini ditangani oleh aplikasi `main`. Di `main/urls.py`, path `"projects/"` dicocokkan dan diarahkan ke fungsi view `show_projects`. View ini mengambil seluruh data dari model `Project` lewat `Project.objects.all()`, memasukkannya ke dalam sebuah context (dictionary), lalu memanggil `render()` dengan template `projects.html` dan context tersebut. Template kemudian memproses context itu menggunakan Django Template Language (`{% for %}`, `{{ }}`, `{% empty %}`) untuk membentuk HTML akhir, yang dikirim balik oleh Django sebagai response ke browser pengguna.

2. Data sebaiknya disimpan di model, bukan ditulis langsung di template, karena model merepresentasikan sumber data yang terpusat dan konsisten. Jika data ditulis langsung di HTML (hardcode), setiap kali ada penambahan atau perubahan data (misalnya proyek baru), saya harus mengedit file template secara manual dan berisiko salah tempat atau format tidak konsisten antar-card. Dengan model, data cukup ditambahkan lewat database (baik lewat Django shell, admin, maupun command khusus), sementara template hanya perlu tahu cara menampilkan data apa pun yang ada tanpa perlu diubah lagi. Ini membuat aplikasi lebih mudah dikembangkan (misalnya menambah field baru di satu tempat) dan lebih mudah dipelihara karena logika tampilan (template) terpisah dari logika data (model).

3. `makemigrations` membaca perubahan yang saya buat pada `models.py` (misalnya menambah model atau field baru) dan menghasilkan berkas migrasi baru di folder `migrations/` yang mendeskripsikan perubahan tersebut dalam bentuk instruksi, tanpa langsung mengubah database. `migrate` kemudian membaca berkas migrasi tersebut (baik yang baru maupun yang belum diterapkan sebelumnya) dan benar-benar menjalankan perubahan itu ke database yang sedang dipakai. Contoh pada tugas ini: saat saya menambahkan model `Project` baru di `main/models.py`, saya menjalankan `python manage.py makemigrations main` yang menghasilkan `main/migrations/0002_project.py`, lalu menjalankan `python manage.py migrate` supaya tabel `Project` benar-benar terbentuk di database SQLite lokal saya.

### AI Disclosure Tugas 2

Pada Tugas 2, saya meminta bantuan Claude untuk membantu saya mengerjakan implementasi fitur Projects secara langsung, atas permintaan saya sendiri, karena saya ingin memahami dulu pola MVT-nya lewat contoh nyata sebelum mencoba membuatnya sendiri di bagian lain. Bagian yang dikerjakan AI meliputi: penambahan model `Project` di `main/models.py`, view `show_projects`, route baru di `main/urls.py`, serta template `projects.html`, Saya memberikan data asli proyek saya (Veto) sebagai konten, lalu memverifikasi hasilnya dengan menjalankan `python manage.py test` (11 test lulus) dan `python manage.py runserver` untuk mengecek halaman `/`, `/experience/`, dan `/projects/` benar-benar tampil dan berfungsi seperti yang diharapkan sebelum saya commit dan push sendiri.


