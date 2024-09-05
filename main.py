import cv2
import numpy as np

def mesajı_bine_çevir(msg):
    if type(msg) == str:
        return ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        return [format(i, "08b") for i in msg]
    elif type(msg) == int or type(msg) == np.uint8:
        return format(msg, "08b")
    else:
        raise TypeError("Desteklenmeyen giriş türü")

def veriyi_gizle(img, gizli_mesaj):
    nBytes = img.shape[0] * img.shape[1] * 3 // 8
    print("Kodlama için Maksimum Byte Sayısı:", nBytes)

    if len(gizli_mesaj) > nBytes:
        raise ValueError("Hata: Yetersiz byte, daha büyük bir resim veya daha az veri gerekli!")

    gizli_mesaj += '#####'
    dataIndex = 0
    bin_gizli_mesaj = mesajı_bine_çevir(gizli_mesaj)

    dataLen = len(bin_gizli_mesaj)
    for values in img:
        for pixels in values:
            r, g, b = mesajı_bine_çevir(pixels)

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

def veriyi_göster(img):
    bin_data = ""
    for values in img:
        for pixels in values:
            r, g, b = mesajı_bine_çevir(pixels)
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

def metni_kodla(img):
    data = input("Kodlanacak veriyi girin: ")
    if len(data) == 0:
        raise ValueError('Hata: Veri boş')

    dosya_adı = input("Yeni kodlanmış resmin adını (uzantısı ile birlikte) girin: ")
    kodlanmış_resim = veriyi_gizle(img.copy(), data)
    cv2.imwrite(dosya_adı, kodlanmış_resim)
    print(f"Kodlanmış resim {dosya_adı} olarak kaydedildi")

def metni_çöz(img):
    text = veriyi_göster(img)
    print(f"Çözülen mesaj: {text}")

def steganografi():
    resim_adı = input("Resmin adını (uzantısı ile birlikte) girin: ")
    resim = cv2.imread(resim_adı)

    print("Resmin şekli: ", resim.shape)
    yeniden_boyutlandırılmış_resim = cv2.resize(resim, (500, 500))
    cv2.imshow('Orijinal Resim', yeniden_boyutlandırılmış_resim)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    while True:
        secim = int(input("Steganografi\n1. Veriyi Kodla\n2. Veriyi Çöz\n3. Çıkış\nSeçeneği girin: "))

        if secim == 1:
            print("\nKodlama...")
            metni_kodla(resim)

        elif secim == 2:
            print("\nÇözme...")
            metni_çöz(resim)

        elif secim == 3:
            print("Çıkılıyor...")
            break

        else:
            print("Geçersiz seçenek. Lütfen 1, 2 veya 3 girin.")

if __name__ == "__main__":
    steganografi()
