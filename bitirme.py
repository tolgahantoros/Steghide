import cv2
import numpy as np
import hashlib
import tkinter as tk
from tkinter import filedialog

class SteganografiArayuz:
    def __init__(self, master):
        self.master = master
        master.title("Steganografi Uygulaması")

        self.resim_etiket = tk.Label(master, text="Resim:")
        self.resim_etiket.grid(row=0, column=0, padx=10, pady=10)

        self.resim_giris = tk.Entry(master, width=50)
        self.resim_giris.grid(row=0, column=1, padx=10, pady=10)

        self.resim_sec_button = tk.Button(master, text="Resim Seç", command=self.resim_sec)
        self.resim_sec_button.grid(row=0, column=2, padx=10, pady=10)

        self.metin_etiket = tk.Label(master, text="Metin:")
        self.metin_etiket.grid(row=1, column=0, padx=10, pady=10)

        self.metin_giris = tk.Entry(master, width=50)
        self.metin_giris.grid(row=1, column=1, padx=10, pady=10)

        self.secim_etiket = tk.Label(master, text="İşlem Seçin:")
        self.secim_etiket.grid(row=2, column=0, padx=10, pady=10)

        self.secim = tk.IntVar()
        self.secim.set(1)

        self.kodla_radio = tk.Radiobutton(master, text="1. Veriyi Kodla", variable=self.secim, value=1)
        self.kodla_radio.grid(row=2, column=1, padx=10, pady=10)

        self.coz_radio = tk.Radiobutton(master, text="2. Veriyi Çöz", variable=self.secim, value=2)
        self.coz_radio.grid(row=2, column=2, padx=10, pady=10)

        self.islem_button = tk.Button(master, text="İşlemi Gerçekleştir", command=self.islemi_gercekle)
        self.islem_button.grid(row=3, column=1, pady=10)

        self.sonuc_etiket = tk.Label(master, text="")
        self.sonuc_etiket.grid(row=4, column=1, pady=10)

    def resim_sec(self):
        dosya_yolu = filedialog.askopenfilename(initialdir=".", title="Resim Seç",
                                                filetypes=(("JPEG files", "*.jpg;*.jpeg"),
                                                           ("PNG files", "*.png"),
                                                           ("All files", "*.*")))
        self.resim_giris.delete(0, tk.END)
        self.resim_giris.insert(0, dosya_yolu)

    def islemi_gercekle(self):
        resim_adı = self.resim_giris.get()

        # Resim yüklenemediyse uyarı göster ve işlemi durdur
        if not resim_adı:
            self.sonuc_etiket.config(text="Hata: Lütfen bir resim seçin.")
            return

        resim = cv2.imread(resim_adı)

        if resim is None:
            self.sonuc_etiket.config(text="Hata: Resim yüklenemedi.")
            return

        if self.secim.get() == 1:
            self.kodla(resim)
        elif self.secim.get() == 2:
            self.coz(resim)

    def kodla(self, img):
        metin = self.metin_giris.get()
        if not metin:
            self.sonuc_etiket.config(text="Hata: Metin girmelisiniz.")
            return

        md5_encoded = hashlib.md5(metin.encode()).hexdigest()

        dosya_adı = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
        kodlanmış_resim = self.veriyi_gizle(img.copy(), md5_encoded)
        cv2.imwrite(dosya_adı, kodlanmış_resim)
        self.sonuc_etiket.config(text=f"Kodlanmış resim {dosya_adı} olarak kaydedildi")

    def coz(self, img):
        text = self.veriyi_göster(img)
        decoded_md5 = hashlib.md5(text.encode()).hexdigest()
        self.sonuc_etiket.config(text=f"Çözülen MD5: {decoded_md5}")

    def mesajı_bine_çevir(self, msg):
        if type(msg) == str:
            return ''.join([format(ord(i), "08b") for i in msg])
        elif type(msg) == bytes or type(msg) == np.ndarray:
            return [format(i, "08b") for i in msg]
        elif type(msg) == int or type(msg) == np.uint8:
            return format(msg, "08b")
        else:
            raise TypeError("Desteklenmeyen giriş türü")

    def veriyi_gizle(self, img, gizli_mesaj):
        nBytes = img.shape[0] * img.shape[1] * 3 // 8
        print("Kodlama için Maksimum Byte Sayısı:", nBytes)

        if len(gizli_mesaj) > nBytes:
            raise ValueError("Hata: Yetersiz byte, daha büyük bir resim veya daha az veri gerekli!")

        gizli_mesaj += '#####'
        dataIndex = 0
        bin_gizli_mesaj = self.mesajı_bine_çevir(gizli_mesaj)

        dataLen = len(bin_gizli_mesaj)
        for values in img:
            for pixels in values:
                r, g, b = self.mesajı_bine_çevir(pixels)

                if dataIndex < dataLen:
                    pixels[0] = int(r[:-1] + bin_gizli_mesaj[dataIndex], 2)
                    dataIndex += 1
                if dataIndex < dataLen:
                    pixels[1] = int(g[:-1] + bin_gizli_mesaj[dataIndex], 2)
                    dataIndex += 1
                if dataIndex < dataLen:
                    pixels[2] = int(b[:-1] + bin_gizli_mesaj[dataIndex], 2)
                    dataIndex += 1

                if dataIndex >= dataLen:
                    break

        return img

    def veriyi_göster(self, img):
        bin_data = ""
        for values in img:
            for pixels in values:
                r, g, b = self.mesajı_bine_çevir(pixels)
                bin_data += r[-1]
                bin_data += g[-1]
                bin_data += b[-1]

        allBytes = [bin_data[i: i + 8] for i in range(0, len(bin_data), 8)]

        decodedData = ""
        for bytes in allBytes:
            decodedData += chr(int(bytes, 2))
            if decodedData[-5:] == "#####":
                break

        return decodedData[:-5]

def main():
    root = tk.Tk()
    app = SteganografiArayuz(root)
    root.mainloop()

if __name__ == "__main__":
    main()
