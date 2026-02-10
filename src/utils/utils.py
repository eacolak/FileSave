import os
import cv2
import csv
import numpy as np
from datetime import datetime
from PIL import Image as PILImage
from sdks.novavision.src.media.image import Image
import requests
import uuid
import base64
import io


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

    print(f"suffix_config: {suffix_config}")

    name_part, given_ext = os.path.splitext(base_name)
    base = name_part if given_ext.lower() == ext.lower() else base_name

    if suffix_config == "timeStamp":
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        final_name = f"{base}_{timestamp}{ext}"
    elif suffix_config == "count":
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

    if not os.path.exists(directory):
        os.makedirs(directory)

    image_data = img_obj.value

    if isinstance(image_data, np.ndarray):
        if image_data.size == 0:
            return "Error: Empty Image Data"

        if image_data.dtype == np.float32:
            if image_data.max() <= 1.0:
                image_data = (image_data * 255).astype(np.uint8)
            else:
                image_data = image_data.astype(np.uint8)
        elif image_data.dtype != np.uint8:
            image_data = image_data.astype(np.uint8)

        success = cv2.imwrite(full_path, image_data)

        if not success:
            raise IOError(f"Failed to save image to {full_path}")
    else:
        raise ValueError(f"The incoming data is not a matrix:  {type(image_data)}")

    return f"Image saved: {full_path}"



def save_csv_local(context_data, local_path, base_file_name, suffix_config, bootstrap, header_config):
    if not local_path:
        raise ValueError("Local Path is required for CSV.")

    final_file_name = generate_file_name(base_file_name, ".csv", suffix_config, bootstrap)
    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    rows_to_write = []

    if isinstance(context_data, list):
        for item in context_data:
            if isinstance(item, dict):
                rows_to_write.append(item)
            elif hasattr(item, "__dict__"):
                rows_to_write.append(item.__dict__)
            else:
                rows_to_write.append({"value": str(item)})

    elif isinstance(context_data, dict):
        rows_to_write.append(context_data)

    elif hasattr(context_data, "__dict__"):
        rows_to_write.append(context_data.__dict__)

    else:
        rows_to_write.append({"raw_data": str(context_data)})


    if not rows_to_write:
        return {
            "status": "skipped",
            "message": "Empty data provided",
            "file_path": full_path
        }

    try:
        file_exists = os.path.isfile(full_path)

        all_keys = set()
        for row in rows_to_write:
            all_keys.update(row.keys())

        fieldnames = sorted(list(all_keys))

        with open(full_path, mode="a", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')

            if header_config == "enable" and not file_exists:
                writer.writeheader()

            count = 0
            for row in rows_to_write:
                writer.writerow(row)
                count += 1


        return {
            "status": "success",
            "message": f"{count} rows appended successfully",
            "file_path": full_path,
            "saved_count": count
        }

    except Exception as e:
        raise IOError(f"Failed to write CSV: {e}")


def save_image_storage(self, img_obj, base_file_name, suffix_config, bootstrap):
    if img_obj is None:
        raise ValueError("img_obj is None")

    try:
        img_encoded = Image.encode64(img_obj)
        img_bytes = base64.b64decode(img_encoded.value)
        img_pill = PILImage.open(io.BytesIO(img_bytes))
        temp_dir = "/storage/temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        ext = MIME_TO_EXT.get(img_obj.mimeType.lower(), ".png")
        final_file_name = generate_file_name(base_file_name, ext, suffix_config, bootstrap)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}{ext}")
        img_pill.save(temp_path)
        api_endpoint = f"{self.environment.web_api}/storage/default/upload?access-token={self.environment.device_access_token}"

        with open(temp_path, "rb") as f:
            files = {"file": f}
            response = requests.post(api_endpoint, files=files, data={"title": final_file_name})

        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"The temp file could not be deleted: {e}")

        if response.status_code == 200:
            return f"Storage Upload Success: {response.text}"
        else:
            return f"Storage Upload Failed: {response.status_code} - {response.text}"

    except Exception as e:
        raise Exception(f"save_image_storage Error: {str(e)}")
