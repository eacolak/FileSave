import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

from sdks.novavision.src.media.image import Image
from sdks.novavision.src.base.component import Component
from sdks.novavision.src.helper.executor import Executor
from components.FileSave.src.models.PackageModel import PackageModel
from components.FileSave.src.utils.response import build_response
from components.FileSave.src.utils.utils import generate_file_name, save_image, save_csv



class FileSave(Component):
    def __init__(self, request, bootstrap):
        super().__init__(request,bootstrap)
        self.request.model = PackageModel(**(self.request.data))
        self.fileType = self.request.get_param("ConfigFileType")
        self.targetDirectory = self.request.get_param("ConfigTargetDirectory") # local,storage
        self.fileName = self.request.get_param("ConfigFileName") # str
        self.images = self.request.get_param("inputImage")
        self.name_suffix_config = self.request.get_param("ConfigfileNameSuffix")
        self.mime_to_ext = {
            "image/png": ".png",
            "image/jpg": ".jpg",
            "image/jpeg": ".jpg",
            "image/gif": ".png"
        }

    @staticmethod
    def bootstrap(config: dict) -> dict:
        return {
            "index": 0
        }

    def run(self):
        self.output_message = ""
        if self.fileType == "csv":
            self.context = self.request.get_param("inputContent")
            self.output_message = self.save_csv() # csv işlemlerini çağır ### Header kontrolü yapılacak
        else:
            # self.save_image() # image işlemlerini çağır
            self.images = self.request.get_param("inputContent")
            img = Image.get_frame(img=self.images, redis_db=self.redis_db)
            self.output_message = self.save_image(img)
        return  build_response(context=self)

if "__main__" == __name__:
    Executor(sys.argv[1]).run()

