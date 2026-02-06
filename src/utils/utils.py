import os
import cv2
import csv
import numpy as np
from datetime import datetime

MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpg": ".jpg",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff"
}


def generate_file_name(base_name: str, ext: str, suffix_config: str, bootstrap: dict) -> str:
    if not base_name:
        base_name = "output"

    name_part, given_ext = os.path.splitext(base_name)
    base = name_part if given_ext.lower() == ext.lower() else base_name

    if suffix_config == "TimeStamp":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        final_name = f"{base}_{timestamp}{ext}"
    elif suffix_config == "Count":
        idx = bootstrap.get("index", 0)
        final_name = f"{base}_{idx:04d}{ext}"
        bootstrap["index"] = idx + 1
    else:
        final_name = f"{base}{ext}"

    return final_name


def save_image_local(img_obj, local_path, base_file_name, suffix_config, bootstrap):
    if img_obj is None:
        raise ValueError("img_obj is None")

    ext = MIME_TO_EXT.get(img_obj.mimeType.lower(), ".png")
    final_file_name = generate_file_name(base_file_name, ext, suffix_config, bootstrap)

    if not local_path:
        raise ValueError("Local Path is required.")

    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except Exception as e:
        raise e

    try:
        image_data = img_obj.value
    except AttributeError:
        raise

    if isinstance(image_data, np.ndarray):
        if image_data.size == 0:
            return "Error: Empty Image"

        if image_data.dtype == np.float32 and image_data.max() <= 1.0:
            image_data = (image_data * 255).astype(np.uint8)
        elif image_data.dtype != np.uint8:
            image_data = image_data.astype(np.uint8)

        success = cv2.imwrite(full_path, image_data)

        if not success:
            raise IOError(f"Failed to save image to {full_path}")
    else:
        raise ValueError("Image data is not a valid numpy array.")

    return f"Image saved: {full_path}"


def save_csv_local(context_data, local_path, base_file_name, suffix_config, bootstrap, header_config):
    if not local_path:
        raise ValueError("Local Path is required for CSV.")

    print(f"[DEBUG] save_csv_local Basladi. Gelen Veri Tipi: {type(context_data)}")

    final_file_name = generate_file_name(base_file_name, ".csv", suffix_config, bootstrap)
    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    # --- VERİ HAZIRLAMA ---
    rows_to_write = []

    # 1. Eğer gelen veri LİSTE ise (BoundingBox listesi gibi)
    if isinstance(context_data, list):
        # Listenin içindeki her bir öğeyi kontrol et
        for item in context_data:
            if isinstance(item, dict):
                rows_to_write.append(item)
            elif hasattr(item, "__dict__"):
                rows_to_write.append(item.__dict__)
            else:
                rows_to_write.append({"value": str(item)})

    # 2. Eğer gelen veri SÖZLÜK ise (Tek bir resim metadatası gibi)
    elif isinstance(context_data, dict):
        rows_to_write.append(context_data)

    # 3. Eğer gelen veri BİR OBJE ise
    elif hasattr(context_data, "__dict__"):
        rows_to_write.append(context_data.__dict__)

    # 4. Hiçbiri değilse
    else:
        rows_to_write.append({"raw_data": str(context_data)})

    print(f"[DEBUG] Yazilacak satir sayisi: {len(rows_to_write)}")

    if not rows_to_write:
        return {
            "status": "skipped",
            "message": "Empty data provided",
            "file_path": full_path
        }

    try:
        file_exists = os.path.isfile(full_path)

        # Tüm satırlardaki bütün olası keyleri topla (Dinamik Sütunlar)
        all_keys = set()
        for row in rows_to_write:
            all_keys.update(row.keys())

        # Sütunları alfabetik sırala ki her seferinde karışık gelmesin
        fieldnames = sorted(list(all_keys))

        with open(full_path, mode="a", newline='', encoding="utf-8") as csvfile:
            # extrasaction='ignore' -> Veride olup fieldnames'de olmayan varsa patlama
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

            # Dosya yeni oluşturuluyorsa veya üzerine yazılmıyorsa başlık ekle
            if header_config == "enable" and not file_exists:
                print(f"[DEBUG] Header yaziliyor: {fieldnames}")
                writer.writeheader()

            count = 0
            for row in rows_to_write:
                writer.writerow(row)
                count += 1

            print(f"[SUCCESS] {count} satir eklendi: {full_path}")

        return {
            "status": "success",
            "message": f"{count} rows appended successfully",
            "file_path": full_path,
            "saved_count": count
        }

    except Exception as e:
        print(f"[ERROR] CSV yazma hatasi: {e}")
        raise IOError(f"Failed to write CSV: {e}")