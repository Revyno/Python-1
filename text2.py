import heapq
from collections import Counter
import json

class Simpul:
    def __init__(self, karakter=None, frekuensi=0):
        self.karakter = karakter
        self.frekuensi = frekuensi
        self.kiri = None
        self.kanan = None

    def __lt__(self, simpul_lain):
        return self.frekuensi < simpul_lain.frekuensi


def bangun_pohon_huffman(teks):
    frekuensi_karakter = Counter(teks)
    antrian = [Simpul(karakter, frekuensi) for karakter, frekuensi in frekuensi_karakter.items()]
    heapq.heapify(antrian)

    while len(antrian) > 1:
        simpul_1 = heapq.heappop(antrian)
        simpul_2 = heapq.heappop(antrian)

        simpul_gabungan = Simpul(frekuensi=simpul_1.frekuensi + simpul_2.frekuensi)
        simpul_gabungan.kiri = simpul_1
        simpul_gabungan.kanan = simpul_2

        heapq.heappush(antrian, simpul_gabungan)

    return antrian[0]

def buat_kode_huffman(simpul, awalan='', peta_kode={}):
    if simpul is None:
        return

    if simpul.karakter is not None:
        peta_kode[simpul.karakter] = awalan

    buat_kode_huffman(simpul.kiri, awalan + '0', peta_kode)
    buat_kode_huffman(simpul.kanan, awalan + '1', peta_kode)

    return peta_kode

def kompresi_huffman(teks):
    if not teks:
        return '', {}

    akar = bangun_pohon_huffman(teks)
    kode_huffman = buat_kode_huffman(akar)
    teks_terkompresi = ''.join(kode_huffman[karakter] for karakter in teks)

    return teks_terkompresi, kode_huffman

def dekompresi_huffman(teks_biner, kode_huffman):
    kode_terbalik = {kode: karakter for karakter, kode in kode_huffman.items()}
    teks_terdekompresi = ''
    kode_sementara = ''

    for bit in teks_biner:
        kode_sementara += bit
        if kode_sementara in kode_terbalik:
            teks_terdekompresi += kode_terbalik[kode_sementara]
            kode_sementara = ''

    return teks_terdekompresi

def hitung_ukuran_dalam_bit(teks, mode='karakter'):
    if mode == 'karakter':
        return len(teks) * 8  # 1 karakter = 8 bit
    elif mode == 'biner':
        return len(teks)      # sudah dalam bit

def tampilkan_menu():
    print("\n=== Program Kompresi Huffman ===")
    print("1. Kompresi teks")
    print("2. Dekompresi teks biner")
    print("3. Keluar")

def main():
    while True:
        tampilkan_menu()
        pilihan = input("Masukkan pilihan (1/2/3): ")

        if pilihan == '1':
            print("\n=== Mode Kompresi ===")
            teks_awal = input("Masukkan teks yang akan dikompresi: ")
            
            if not teks_awal:
                print("Teks tidak boleh kosong!")
                continue
                
            hasil_kompresi, peta_kode = kompresi_huffman(teks_awal)
            ukuran_awal = hitung_ukuran_dalam_bit(teks_awal, mode='karakter')
            ukuran_kompresi = hitung_ukuran_dalam_bit(hasil_kompresi, mode='biner')
            rasio_kompresi = ukuran_kompresi / ukuran_awal * 100

            print("\nHasil Kompresi:")
            print("Teks Asli:", teks_awal)
            print("Teks Terkompresi:", hasil_kompresi)
            print("Ukuran Teks Asli:", ukuran_awal, "bit")
            print("Ukuran Setelah Kompresi:", ukuran_kompresi, "bit")
            print(f"Rasio Kompresi: {rasio_kompresi:.2f}%")
            
            # Simpan kode Huffman untuk dekompresi
            with open('kode_huffman.json', 'w') as f:
                json.dump(peta_kode, f)
            print("\nKode Huffman telah disimpan di 'kode_huffman.json'")

        elif pilihan == '2':
            print("\n=== Mode Dekompresi ===")
            teks_biner = input("Masukkan teks biner yang akan didekompresi: ")
            
            try:
                with open('kode_huffman.json', 'r') as f:
                    peta_kode = json.load(f)
            except FileNotFoundError:
                print("Error: File kode_huffman.json tidak ditemukan.")
                print("Pastikan Anda telah melakukan kompresi terlebih dahulu.")
                continue
                
            hasil_dekompresi = dekompresi_huffman(teks_biner, peta_kode)
            print("\nHasil Dekompresi:", hasil_dekompresi)

        elif pilihan == '3':
            print("Terima kasih telah menggunakan program ini!")
            break

        else:
            print("Pilihan tidak valid. Silakan pilih 1, 2, atau 3.")

if __name__ == '__main__':
    main()