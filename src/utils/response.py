from sdks.novavision.src.helper.package import PackageHelper
from components.FileSave.src.models.PackageModel import (
    PackageModel, PackageConfigs, ConfigExecutor,
    ImageSave, ImageResponse, ImageOutputs,
    CSVSave, CSVResponse, CSVOutputs,
    OutputText
)


def build_image_save_response(context):
    output_text = OutputText(value=context.output_message)
    image_outputs = ImageOutputs(outputText=output_text)
    image_response = ImageResponse(outputs=image_outputs)
    image_executor = ImageSave(value=image_response)
    config_executor = ConfigExecutor(value=image_executor)
    package_configs = PackageConfigs(executor=config_executor)
    package = PackageHelper(
        packageModel=PackageModel,
        packageConfigs=package_configs
    )
    return package.build_model(context)


def build_csv_save_response(context):
    output_text = OutputText(value=context.output_message)
    csv_outputs = CSVOutputs(outputData=output_text)
    csv_response = CSVResponse(outputs=csv_outputs)
    csv_executor = CSVSave(value=csv_response)
    config_executor = ConfigExecutor(value=csv_executor)
    package_configs = PackageConfigs(executor=config_executor)
    package = PackageHelper(
        packageModel=PackageModel,
        packageConfigs=package_configs
    )
    return package.build_model(context)