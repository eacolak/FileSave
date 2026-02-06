import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.FileSave.src.models.PackageModel import PackageModel
from components.FileSave.src.utils.response import build_response
# İki fonksiyonu da import ediyoruz
from components.FileSave.src.utils.utils import save_image_local, save_csv_local


class FileSave(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.targetDirectory = self.request.get_param("ConfigTargetDirectory")
        self.fileName = self.request.get_param("ConfigFileName")
        self.suffix_config = self.request.get_param("ConfigfileNameSuffix")
        self.localPath = self.request.get_param("LocalPath")
        self.filetype = self.request.get_param("ConfigFileType")
        self.inputContent = self.request.get_param("inputContent")
        self.headerConfig = self.request.get_param("ConfigHeader")

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {
            "index": 0
        }

    def run(self):
        self.output_message = ""

        # --- CSV MODU ---
        if self.filetype == "csv":
            try:
                # CSV için inputContent'in bir Dictionary (Sözlük) olması beklenir.
                # Örn: {"isim": "Ali", "yas": 25}
                self.output_message = save_csv_local(
                    context_data=self.inputContent,
                    local_path=self.localPath,
                    base_file_name=self.fileName,
                    suffix_config=self.suffix_config,
                    bootstrap=self.bootstrap,
                    header_config=self.headerConfig
                )
            except Exception as e:
                self.output_message = f"CSV Error: {str(e)}"

        # --- IMAGE MODU (Mevcut Çalışan Kodun) ---
        else:
            # Sadece image modunda Image.get_frame çağırıyoruz
            img = Image.get_frame(img=self.inputContent, redis_db=self.redis_db)
            if img:
                self.output_message = save_image_local(
                    img_obj=img,
                    local_path=self.localPath,
                    base_file_name=self.fileName,
                    suffix_config=self.suffix_config,
                    bootstrap=self.bootstrap
                )
            else:
                self.output_message = "No image data found to save."

        return build_csv_save_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()