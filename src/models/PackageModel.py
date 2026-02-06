from pydantic import Field, validator, model_validator
from typing import List, Optional, Union, Any, Dict,Literal
from sdks.novavision.src.base.model import Package, Image, Param, Inputs, Configs, Outputs, Response, Request,Output,Input,Config


class InputData(Input):
    name: Literal["inputData"] = "inputData"
    value: Union[list, dict, str]
    type: str = "object"

    @model_validator(mode="after")
    def set_type(self):
        if isinstance(self.value, str):
            self.type = "string"
        elif isinstance(self.value, (list, dict)):
            self.type = "object"
        return self

    class Config:
        title = "Data"


class OutputText(Output):
    name: Literal["outputText"] = "outputText"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Text"


class InputContent(Input):
    name: Literal["inputContent"] = "inputContent"
    value: Union[List[Image], Image, Dict]
    type: str = ""

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"

    class Config:
        title = "Image"


class ConfigHeaderEnable(Config):
    name: Literal["ConfigHeaderEnable"] = "ConfigHeaderEnable"
    value: Literal["enable"] = "enable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    class Config:
        title = "Enable"


class ConfigHeaderDisable(Config):
    name: Literal["ConfigHeaderDisable"] = "ConfigHeaderDisable"
    value: Literal["disable"] = "disable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Disable"


class ConfigHeader(Config):
    """
    Determines whether to write the column names as the first row in the CSV file.
    """
    name: Literal["ConfigHeader"] = "ConfigHeader"
    value: Union[ConfigHeaderEnable,ConfigHeaderDisable]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"

    class Config:
        title="Header"
        json_schema_extra = {
            "shortDescription": "Include Column Headers"
        }


class TargetStorage(Config):
    name: Literal["TargetStorage"] = "TargetStorage"
    value: Literal["storage"] = "storage"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Storage"


class LocalPath(Config):
    """
    The absolute path on the local file system where the file will be saved.
    Example: C:/Users/Admin/Documents/
    """
    name: Literal["LocalPath"] = "LocalPath"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Local Path"
        json_schema_extra = {
            "shortDescription": "Absolute System Path"
        }


class TargetLocal(Config):
    name: Literal["TargetLocal"] = "TargetLocal"
    value: Literal["local"] = "local"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    localPath: LocalPath

    class Config:
        title = "Local"


class ConfigTargetDirectory(Config):
    """
    Choose where to save the file.
    - Storage: Uses the system's internal managed storage.
    - Local: Allows saving to a custom path on the OS.
    """
    name: Literal["ConfigTargetDirectory"] = "ConfigTargetDirectory"
    value: Union[TargetStorage, TargetLocal]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Target Directory"
        json_schema_extra = {
            "shortDescription": "Destination Location"
        }


class TimeStamp(Config):
    name: Literal["TimeStamp"] = "TimeStamp"
    value: Literal["TimeStamp"] = "TimeStamp"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Time Stamp"


class Count(Config):
    name: Literal["Count"] = "Count"
    value: Literal["Count"] = "Count"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Count"


class ConfigfileNameSuffix(Config):
    """
    Appends a suffix to the filename to prevent overwriting.
    - TimeStamp: Adds the date and time (e.g., file_20231025.jpg).
    - Count: Adds an incremental number (e.g., file_01.jpg, file_02.jpg).
    """
    name: Literal["ConfigfileNameSuffix"] = "ConfigfileNameSuffix"
    value: Union[TimeStamp, Count]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"

    class Config:
        title = "Name Suffix"
        json_schema_extra = {
            "shortDescription": "Naming Convention"
        }


class ConfigFileName(Config):
    """
    The base name of the file (without extension or suffix).
    e.g., entering 'result' creates 'result_01.jpg'.
    """
    name: Literal["ConfigFileName"] = "ConfigFileName"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "File Name"
        json_schema_extra = {
            "shortDescription": "Base Filename"
        }



class ImageInputs(Inputs):
    inputContent: InputContent


class ImageConfigs(Configs):
    configTargetDirectory: ConfigTargetDirectory
    configFileName: ConfigFileName
    configfileNameSuffix: ConfigfileNameSuffix


class ImageRequest(Request):
    inputs: Optional[ImageInputs]
    configs: ImageConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }


class ImageOutputs(Outputs):
    outputText: OutputText


class ImageResponse(Response):
    outputs: ImageOutputs


class ImageExecutor(Config):
    name: Literal["ImageSave"] = "ImageSave"
    value: Union[ImageRequest, ImageResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Image Save"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }



class CSVInputs(Inputs):
    inputData: InputData


class CSVConfigs(Configs):
    configTargetDirectory: ConfigTargetDirectory
    configFileName: ConfigFileName
    configHeader: ConfigHeader
    configfileNameSuffix: ConfigfileNameSuffix


class CSVRequest(Request):
    inputs: Optional[CSVInputs]
    configs: CSVConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }


class CSVOutputs(Outputs):
    outputText: OutputText


class CSVResponse(Response):
    outputs: CSVOutputs


class CSVExecutor(Config):
    name: Literal["CSVSave"] = "CSVSave"
    value: Union[CSVRequest, CSVResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "CSV Save"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }

class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[ImageExecutor, CSVExecutor]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "File Type"
        json_schema_extra = {
            "shortDescription": "File Type"
        }


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["FileSave"] = "FileSave"