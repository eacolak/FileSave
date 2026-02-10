import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.FileSave.src.models.PackageModel import PackageModel
from components.FileSave.src.utils.response import build_image_save_response
from components.FileSave.src.utils.utils import save_image_local, save_image_storage


class ImageSave(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.targetDirectory = self.request.get_param("ConfigTargetDirectory")
        self.fileName = self.request.get_param("ConfigFileName")
        self.suffix_config = self.request.get_param("ConfigFileNameSuffix")
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
        if (self.targetDirectory == "local"):
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




        else:
            img = Image.get_frame(img=self.inputContent, redis_db=self.redis_db)

            if img:
                self.output_message = save_image_storage(
                    self=self,
                    img_obj=img,
                    base_file_name=self.fileName,
                    suffix_config=self.suffix_config,
                    bootstrap=self.bootstrap
                )
            else:
                self.output_message = "No image data found to save."

        return build_image_save_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()