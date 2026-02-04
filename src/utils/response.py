from sdks.novavision.src.helper.package import PackageHelper
from components.FileSave.src.models.PackageModel import OutputText, FileSaveOutputs, FileSaveResponse, FileSaveExecutor, ConfigExecutor, PackageConfigs, PackageModel

def build_response(context):
    outputText = OutputText(value=context.output_message)
    fileSaveOutputs = FileSaveOutputs(outputText=outputText)
    imageSaveOutputs = FileSaveResponse(outputs=fileSaveOutputs)
    imageSaveExecutor = FileSaveExecutor(value=imageSaveOutputs)
    executor = ConfigExecutor(value=imageSaveExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel