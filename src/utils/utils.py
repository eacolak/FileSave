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

    final_file_name = generate_file_name(base_file_name, ".csv", suffix_config, bootstrap)
    full_path = os.path.join(local_path, final_file_name)
    directory = os.path.dirname(full_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    rows_to_write = []

    items_to_process = context_data if isinstance(context_data, list) else [context_data]

    for item in items_to_process:
        rows_to_write.append(item.__dict__)

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