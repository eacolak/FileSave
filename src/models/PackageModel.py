from pydantic import Field, validator, model_validator
from typing import List, Optional, Union, Dict, Literal
from sdks.novavision.src.base.model import (
    Package, Image, Inputs, Configs, Outputs,
    Response, Request, Output, Input, Config
)


# --- INPUTS ---

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


class InputContent(Input):
    name: Literal["inputContent"] = "inputContent"
    value: Union[List[Image], Image, Dict]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        val = values.get('value')
        if isinstance(val, Image):
            return "object"
        elif isinstance(val, list):
            return "list"
        elif isinstance(val, dict):
            return "dict"
        return "object"

    class Config:
        title = "Image Content"


# --- OUTPUTS ---

class OutputText(Output):
    name: Literal["outputText"] = "outputText"
    value: str
    type: Literal["string"] = "string"

    class Config:
        title = "Status Message"


# --- CONFIG OPTIONS (Leaf Nodes) ---

class ConfigHeaderEnable(Config):
    name: Literal["configHeaderEnable"] = "configHeaderEnable"
    value: Literal["enable"] = "enable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Enable"


class ConfigHeaderDisable(Config):
    name: Literal["configHeaderDisable"] = "configHeaderDisable"
    value: Literal["disable"] = "disable"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Disable"


class TargetStorage(Config):
    name: Literal["targetStorage"] = "targetStorage"
    value: Literal["storage"] = "storage"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Internal Storage"


class LocalPath(Config):
    name: Literal["LocalPath"] = "LocalPath"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "System Path"
        json_schema_extra = {"shortDescription": "Absolute path on OS"}


class TargetLocal(Config):
    name: Literal["targetLocal"] = "targetLocal"
    value: Literal["local"] = "local"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"
    localPath: LocalPath

    class Config:
        title = "Local File System"


class TimeStamp(Config):
    name: Literal["timeStamp"] = "timeStamp"
    value: Literal["timeStamp"] = "timeStamp"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Time Stamp"


class Count(Config):
    name: Literal["count"] = "count"
    value: Literal["count"] = "count"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Incremental Count"


# --- CONFIG PARAMETERS ---

class ConfigHeader(Config):
    """Determines whether to write column names as the first row."""
    name: Literal["ConfigHeader"] = "ConfigHeader"
    value: Union[ConfigHeaderEnable, ConfigHeaderDisable]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Include Header"
        json_schema_extra = {"shortDescription": "CSV Header Toggle"}


class ConfigTargetDirectory(Config):
    """Choose destination: Managed Storage or Local Path."""
    name: Literal["ConfigTargetDirectory"] = "ConfigTargetDirectory"
    value: Union[TargetStorage, TargetLocal]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Target Location"
        json_schema_extra = {"shortDescription": "Save Destination"}


class ConfigFileNameSuffix(Config):
    """Appends suffix to prevent overwriting files."""
    name: Literal["ConfigFileNameSuffix"] = "ConfigFileNameSuffix"
    value: Union[TimeStamp, Count]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Filename Suffix"
        json_schema_extra = {"shortDescription": "Naming Rule"}


class ConfigFileName(Config):
    """Base name of the file without extension."""
    name: Literal["ConfigFileName"] = "ConfigFileName"
    value: str
    type: Literal["string"] = "string"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Base Filename"
        json_schema_extra = {"shortDescription": "Initial file name"}


# --- EXECUTOR AGGREGATIONS ---

class ImageInputs(Inputs):
    inputContent: InputContent


class ImageConfigs(Configs):
    configTargetDirectory: ConfigTargetDirectory
    configFileName: ConfigFileName
    configFileNameSuffix: ConfigFileNameSuffix


class ImageRequest(Request):
    inputs: Optional[ImageInputs]
    configs: ImageConfigs

    class Config:
        json_schema_extra = {"target": "configs"}


class ImageOutputs(Outputs):
    outputText: OutputText


class ImageResponse(Response):
    outputs: ImageOutputs


class ImageSave(Config):
    name: Literal["ImageSave"] = "ImageSave"
    value: Union[ImageRequest, ImageResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Image"
        json_schema_extra = {"target": {"value": 0}}


class CSVInputs(Inputs):
    inputData: InputData


class CSVConfigs(Configs):
    configTargetDirectory: ConfigTargetDirectory
    configFileName: ConfigFileName
    configHeader: ConfigHeader
    configFileNameSuffix: ConfigFileNameSuffix


class CSVRequest(Request):
    inputs: Optional[CSVInputs]
    configs: CSVConfigs

    class Config:
        json_schema_extra = {"target": "configs"}


class CSVOutputs(Outputs):
    outputText: OutputText


class CSVResponse(Response):
    outputs: CSVOutputs


class CSVSave(Config):
    name: Literal["CSVSave"] = "CSVSave"
    value: Union[CSVRequest, CSVResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "CSV"
        json_schema_extra = {"target": {"value": 0}}


# --- ROOT PACKAGE MODELS ---

class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[ImageSave, CSVSave]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "File Format"
        json_schema_extra = {"shortDescription": "Choose output format"}


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["FileSave"] = "FileSave"