
Perhatikan urutan dari instalasi berikut, karena jika tidak berurutan
akan mempengaruhi keberhasilan jalan program.

1. install python versi 3.9 yang terbaru pada link berikut:
    https://www.python.org/downloads/release/python-390/

    - Pada saat install python checklist "Add Python 3.9 to PATH" lalu klik install
    - Untuk mengecek apakah python telah terinstall kedalam PATH buka Command Prompt
    (cmd) dan ketikkan "python". Apabila kita masuk kedalam console python dan tertuliskan
    versi python yang telah terinstall pada cmd, maka python telah terinstall

2. Buka CMD dan install requirement yang dibutuhkan dengan mengetikkan perintah berikut ke CMD.
    - "pip install -r requirement.txt" -> requirement akan terinstall secara otomatis, tunggu hinggga instalasi selesai.
    - "pip install opencv-python-headless -U"
    - "pip install opencv-contrib-python"

3. instalasi telah selesai, running program main.py untuk menjalankan program.


Instruksi Database

- inisiasi database pada program dapat dilihat pada file "classes.py"

- Struktur dari database untuk masing-masing adalah sebagai berikut:
    - struktur database untuk penyimpanan data hasil ocr harus terdapat kolom
        CameraSource -> VARCHAR
        Code1 -> VARCHAR
        Code2 -> VARCHAR
    
    - struktur database untuk penyimpanan data hasil deteksi truck harus terdapat kolom
        TruckStatus -> VARCHAR
