import os
import io
import cv2
import sys
import csv
import uuid
import base64
import requests
import numpy as np
from datetime import datetime
from PIL import Image as PILImage

def generate_file_name(self, base_name: str, ext: str) -> str:
    name, given_ext = os.path.splitext(base_name)
    # Eğer verilen uzantı, beklenenle aynı değilse, sonradan eklenecek
    if given_ext.lower() == ext:
        base = name  # .csv zaten varsa, onu çıkar
    else:
        base = base_name  # yoksa doğrudan kullan

    # suffix işlemi
    if self.name_suffix_config == "TimeStamp":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{base}-{timestamp}{ext}"
    else:
        if self.bootstrap["index"] == 0:
            file_name = base + ext
        else:
            file_name = f"{base}-{self.bootstrap['index']}{ext}"
        self.bootstrap["index"] += 1
        return file_name


def save_image(self, img):
    if self.targetDirectory == "local":
        # 1. Dosya adı ve tam yol
        ext = self.mime_to_ext.get(img.mimeType.lower(), ".png")
        self.fileName = self.generate_file_name(self.fileName, ext)
        self.localPath = self.request.get_param("LocalPath")
        full_path = os.path.join(self.localPath, self.fileName)

        # 2. Klasör yoksa oluştur
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        image_data = img.value
        # Normalize edilmiş mi?
        if image_data.dtype == np.float32 and image_data.max() <= 1.0:
            image_data = (image_data * 255).astype(np.uint8)
        elif image_data.dtype != np.uint8:
            image_data = image_data.astype(np.uint8)

        # 4. Kaydet
        success = cv2.imwrite(full_path, image_data)
        if not success:
            raise IOError(f"Failed to save image to {full_path}")

        output_message = f"✅ Image saved locally to {full_path}"

    else:
        img = Image.encode64(img)
        img_pill = PILImage.open(io.BytesIO(base64.decodebytes(bytes(img.value, "utf-8"))))
        if not os.path.exists("/storage/temp"):
            os.makedirs("/storage/temp")
        img_path = f"/storage/temp/{uuid.uuid4()}.{img.mimeType.split('/')[-1]}"
        img_pill.save(img_path)
        api_endpoint = f"{self.environment.web_api}/storage/default/upload?access-token={self.environment.device_access_token}"
        ext = self.mime_to_ext.get(img.mimeType.lower(), ".png")
        self.fileName = self.generate_file_name(self.fileName, ext)
        with open(img_path, "rb") as f:
            files = {"file": f}
            response = requests.post(api_endpoint, files=files, data={"title": self.fileName})

        try:
            os.remove(img_path)
        except Exception as e:
            raise Exception(f"ImageSave Error: {e}")
        output_message = response.text

    return output_message


def save_csv(self):
    # output_message = ""
    # print("Csv kaydetme başlatılıyor...")
    # if self.targetDirectory == "local":
    #     print("Parametreler alınıyotur...")
    #     self.localPath = self.request.get_param("LocalPath")
    #     self.header = self.request.get_param("ConfigHeader")  # "enable" or "disable"
    #     print("Parametreler alındı, kaydetme işlemi başlatılıyor...")
    #     print(self.localPath)
    #     print(self.header)
    #     # Klasör yoksa oluştur
    #     if not os.path.exists(os.path.dirname(self.localPath)):
    #         os.makedirs(os.path.dirname(self.localPath))
    #     print("Klasör kontrolü yapıldı...")
    #     # context dictionary'sini hazırla
    #     data = self.context  # örn: {0: "Alice", 1: "30", 2: "London"}
    #     print("Context verisi alındı:", data)
    #     row = list(data.values())
    #     print("Row verisi hazırlandı:", row)
    #     headers = list(data.keys())
    #     print("Header verisi hazırlandı:", headers)
    #
    #     # Dosya zaten var mı?
    #     file_exists = os.path.isfile(self.localPath)
    #     print("Dosya var mı kontrol ediliyor:", file_exists)
    #
    #     # Dosyayı aç, varsa append modunda
    #     with open(self.localPath, mode="a", newline='', encoding="utf-8") as csvfile:
    #         writer = None
    #         print("CSV dosyası açıldı, yazma işlemi başlatılıyor...")
    #         # Header enable ise ve dosya daha önce yoksa, başlıkları yaz
    #         if self.header == "enable" and not file_exists:
    #             print("Header yazılıyor...")
    #             writer = csv.writer(csvfile)
    #             writer.writerow(headers)
    #         print("Row verisi yazılıyor...")
    #         # Veriyi yaz
    #         writer = writer or csv.writer(csvfile)
    #         writer.writerow(row)
    #         output_message = "Çalıştı"

    output_message = ""
    print("Csv kaydetme başlatılıyor...")

    self.fileName = self.generate_file_name(self.fileName, ".csv")

    if self.targetDirectory == "local":
        print("Parametreler alınıyor...")
        self.localPath = self.request.get_param("LocalPath")  # örn: "/storage/logs"
        self.header = self.request.get_param("ConfigHeader")  # "enable" or "disable"

        print(
            "Parametreler alındı, kaydetme işlemi başlatılı                                                                                                                                                                                                                                                                                                                                                            yor...")
        print("Klasör yolu:", self.localPath)
        print("Dosya adı:", self.fileName)
        print("Header durumu:", self.header)

        # Klasör yoksa oluştur
        if not os.path.exists(self.localPath):
            os.makedirs(self.localPath)
            print("Klasör oluşturuldu:", self.localPath)
        else:
            print("Klasör zaten mevcut.")

        # Dosya tam yolu: klasör + dosya adı
        file_path = os.path.join(self.localPath, self.fileName)
        print("Tam dosya yolu:", file_path)

        # context dictionary'sini hazırla
        data = self.context  # örn: {0: "Alice", 1: "30", 2: "London"}
        print("Context verisi alındı:", data)
        row = list(data.values())
        print("Row verisi hazırlandı:", row)
        headers = list(data.keys())
        print("Header verisi hazırlandı:", headers)

        # Dosya zaten var mı?
        file_exists = os.path.isfile(file_path)
        print("Dosya var mı kontrol ediliyor:", file_exists)

        # Dosyayı aç, varsa append modunda
        with open(file_path, mode="a", newline='', encoding="utf-8") as csvfile:
            writer = None
            print("CSV dosyası açıldı, yazma işlemi başlatılıyor...")
            # Header enable ise ve dosya daha önce yoksa, başlıkları yaz
            if self.header == "enable" and not file_exists:
                print("Header yazılıyor...")
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            print("Row verisi yazılıyor...")
            # Veriyi yaz
            writer = writer or csv.writer(csvfile)
            writer.writerow(row)
            output_message = "Çalıştı"
    else:
        pass

    return output_message