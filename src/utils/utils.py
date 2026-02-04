import os
import cv2
import csv  # <--- YENİ EKLENDİ
import numpy as np
from datetime import datetime

# MIME Type haritası
MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpg": ".jpg",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff"
}


def generate_file_name(base_name: str, ext: str, suffix_config: str, bootstrap: dict) -> str:
    print(f"[DEBUG] Dosya ismi olusturuluyor... Base: {base_name}, Ext: {ext}, Suffix: {suffix_config}")

    if not base_name:
        base_name = "output"

    name_part, given_ext = os.path.splitext(base_name)

    if given_ext.lower() == ext.lower():
        base = name_part
    else:
        base = base_name

    if suffix_config == "TimeStamp":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        final_name = f"{base}_{timestamp}{ext}"
    elif suffix_config == "Count":
        idx = bootstrap.get("index", 0)
        final_name = f"{base}_{idx:04d}{ext}"
        bootstrap["index"] = idx + 1
    else:
        final_name = f"{base}{ext}"

    print(f"[DEBUG] Olusturulan dosya ismi: {final_name}")
    return final_name


def save_image_local(img_obj, local_path, base_file_name, suffix_config, bootstrap):
    """
    Detaylı loglama ile görüntüyü kaydeder.
    """
    print("\n" + "=" * 30)
    print("[DEBUG] save_image_local fonksiyonu basladi.")
    print(f"[DEBUG] Gelen local_path: '{local_path}'")

    # 0. Image Objesi Kontrolü
    if img_obj is None:
        print("[ERROR] HATA: img_obj None olarak geldi!")
        raise ValueError("img_obj is None")

    print(f"[DEBUG] Image MimeType: {getattr(img_obj, 'mimeType', 'Bilinmiyor')}")

    # 1. Uzantıyı belirle
    ext = MIME_TO_EXT.get(img_obj.mimeType.lower(), ".png")

    # 2. Dosya ismini oluştur
    final_file_name = generate_file_name(base_file_name, ext, suffix_config, bootstrap)

    # 3. Klasör yolunu kontrol et
    if not local_path:
        print("[ERROR] HATA: local_path parametresi bos!")
        raise ValueError("Local Path is required.")

    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    print(f"[DEBUG] Hedef tam yol (Full Path): {full_path}")
    print(f"[DEBUG] Hedef klasor: {directory}")

    # Klasör yoksa oluştur
    try:
        if not os.path.exists(directory):
            print(f"[DEBUG] Klasor mevcut degil, olusturuluyor: {directory}")
            os.makedirs(directory)
        else:
            print("[DEBUG] Klasor zaten mevcut.")

        # Klasöre yazma izni var mı basit kontrol (opsiyonel)
        if not os.access(directory, os.W_OK):
            print(f"[WARNING] UYARI: Klasore yazma izni (W_OK) yok gibi gorunuyor: {directory}")

    except Exception as e:
        print(f"[ERROR] Klasor olusturma hatasi: {e}")
        raise e

    # 4. Görüntü verisini al
    try:
        image_data = img_obj.value
    except AttributeError:
        print("[ERROR] HATA: img_obj icinde 'value' attribute'u yok!")
        raise

    print(f"[DEBUG] Resim Veri Tipi (Type): {type(image_data)}")

    if isinstance(image_data, np.ndarray):
        print(f"[DEBUG] Resim Boyutu (Shape): {image_data.shape}")
        print(f"[DEBUG] Veri Formatı (Dtype): {image_data.dtype}")
        print(f"[DEBUG] Veri İstatistiği - Min: {image_data.min()}, Max: {image_data.max()}")

        if image_data.size == 0:
            print("[ERROR] HATA: Resim verisi bos (Size is 0)!")
            return "Error: Empty Image"

        # Normalize işlemi
        if image_data.dtype == np.float32 and image_data.max() <= 1.0:
            image_data = (image_data * 255).astype(np.uint8)
        elif image_data.dtype != np.uint8:
            image_data = image_data.astype(np.uint8)

        # 5. Kaydet (OpenCV)
        print("[DEBUG] cv2.imwrite calistiriliyor...")
        success = cv2.imwrite(full_path, image_data)

        if success:
            print(f"[SUCCESS] BASARILI! Dosya suraya yazildi: {full_path}")
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"[DEBUG] Disk kontrolu: Dosya mevcut, boyutu: {size} bytes")
            else:
                print("[ERROR] Gariplik: imwrite True dondu ama dosya diskte bulunamadi!")
        else:
            print(f"[ERROR] HATA: cv2.imwrite 'False' dondu. Yazma basarisiz.")
            raise IOError(f"Failed to save image to {full_path}")

    else:
        print(f"[ERROR] HATA: Gelen veri numpy array degil! Gelen tip: {type(image_data)}")
        raise ValueError("Image data is not a valid numpy array.")

    print("=" * 30 + "\n")
    return f"Image saved: {full_path}"


# --- YENİ EKLENEN CSV FONKSİYONU ---
def save_csv_local(context_data, local_path, base_file_name, suffix_config, bootstrap, header_config):
    """
    Dictionary verisini CSV olarak kaydeder.
    """
    print("\n" + "=" * 30)
    print("[DEBUG] save_csv_local fonksiyonu basladi.")
    print(f"[DEBUG] Veri Tipi: {type(context_data)}")

    # 1. Dosya ismini oluştur (.csv uzantılı)
    final_file_name = generate_file_name(base_file_name, ".csv", suffix_config, bootstrap)

    # 2. Yol Kontrolü
    if not local_path:
        raise ValueError("Local Path is required for CSV.")

    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    # Klasör oluştur
    if not os.path.exists(directory):
        print(f"[DEBUG] Klasor olusturuluyor: {directory}")
        os.makedirs(directory)

    # 3. Veri Kontrolü
    if not isinstance(context_data, dict):
        print(f"[ERROR] CSV icin inputContent DICT olmali. Gelen: {type(context_data)}")
        # Eğer dict değilse string'e çevirip tek sütun gibi kaydetmeyi deneyebiliriz ama şu an hata verelim
        raise ValueError(f"Input content must be a dictionary. Received: {type(context_data)}")

    row_values = list(context_data.values())
    headers = list(context_data.keys())

    # 4. Dosya var mı kontrolü (Header yazıp yazmamak için)
    file_exists = os.path.isfile(full_path)
    print(f"[DEBUG] Hedef dosya var mi? {file_exists}")
    print(f"[DEBUG] Header Config: {header_config}")

    try:
        # append modunda aç ('a')
        with open(full_path, mode="a", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Eğer header açık ise ve dosya daha önce yoksa başlıkları yaz
            if header_config == "enable" and not file_exists:
                print("[DEBUG] Header satiri yaziliyor...")
                writer.writerow(headers)

            print(f"[DEBUG] Veri satiri yaziliyor: {row_values}")
            writer.writerow(row_values)

        print(f"[SUCCESS] CSV basariyla guncellendi: {full_path}")
        return f"Data appended to {full_path}"

    except Exception as e:
        print(f"[ERROR] CSV yazma hatasi: {e}")
        raise IOError(f"Failed to write CSV: {e}")