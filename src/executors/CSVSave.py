import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.FileSave.src.models.PackageModel import PackageModel
from components.FileSave.src.utils.response import build_csv_save_response
from components.FileSave.src.utils.utils import save_image_local, save_csv_local


class CSVSave(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request, bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.targetDirectory = self.request.get_param("ConfigTargetDirectory")
        self.fileName = self.request.get_param("ConfigFileName")
        self.suffix_config = self.request.get_param("ConfigFileNameSuffix")
        self.localPath = self.request.get_param("LocalPath")
        self.headerConfig = self.request.get_param("ConfigHeader")
        self.inputData = self.request.get_param("inputData")

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {
            "index": 0
        }

    def run(self):
        self.output_message = ""

        img = Image.get_frame(img=self.inputData, redis_db=self.redis_db)
        img = Image.encode64(img)

        try:
            self.output_message = save_csv_local(
                context_data=img,
                local_path=self.localPath,
                base_file_name=self.fileName,
                suffix_config=self.suffix_config,
                bootstrap=self.bootstrap,
                header_config=self.headerConfig
            )
        except Exception as e:
            self.output_message = f"CSV Error: {str(e)}"

        return build_csv_save_response(context=self)


if "__main__" == __name__:
    Executor(sys.argv[1]).run()