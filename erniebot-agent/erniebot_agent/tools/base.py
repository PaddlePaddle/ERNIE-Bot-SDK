# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Type

from erniebot_agent.message import Message
from erniebot_agent.tools.schema import (
    Endpoint,
    EndpointInfo,
    RemoteToolView,
    ToolParameterView,
    scrub_dict,
)
from yaml import safe_dump


class BaseTool(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def function_call_schema(self) -> dict:
        raise NotImplementedError


class Tool(BaseTool, ABC):
    description: str
    name: Optional[str] = None
    input_type: Optional[Type[ToolParameterView]] = None
    ouptut_type: Optional[Type[ToolParameterView]] = None

    @property
    def tool_name(self):
        return self.name or self.__class__.__name__

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Dict[str, Any]:
        """the body of tools

        Returns:
            Any:
        """
        raise NotImplementedError

    def function_call_schema(self) -> dict:
        inputs = {
            "name": self.tool_name,
            "description": self.description,
            "examples": [example.to_dict() for example in self.examples],
        }
        if self.input_type is not None:
            inputs["parameters"] = self.input_type.function_call_schema()
        if self.ouptut_type is not None:
            inputs["responses"] = self.ouptut_type.function_call_schema()

        return scrub_dict(inputs) or {}

    @property
    def examples(self) -> List[Message]:
        return []


@dataclass
class RemoteToolkit:
    """plugin schema object which be converted from Toolkit and generate openapi configuration file"""

    name: str

    openapi: str
    info: EndpointInfo
    servers: List[Endpoint]
    paths: List[RemoteToolView]

    component_schemas: dict[str, Type[ToolParameterView]]

    async def __call__(self, **kwargs) -> Dict[str, Any]:
        return {}

    def __post_init__(self):
        pass

    def to_openapi_dict(self) -> dict:
        """convert plugin schema to openapi spec dict"""
        spec_dict = {
            "openapi": self.openapi,
            "info": asdict(self.info),
            "servers": [asdict(server) for server in self.servers],
            "paths": {tool_view.uri: tool_view.to_openapi_dict() for tool_view in self.paths},
            "components": {
                "schemas": {
                    uri: parameters_view.to_openapi_dict()
                    for uri, parameters_view in self.component_schemas.items()
                }
            },
        }
        return scrub_dict(spec_dict, remove_empty_dict=True) or {}

    def to_openapi_file(self, file: str):
        """generate openapi configuration file

        Args:
            file (str): the path of the openapi yaml file
        """
        spec_dict = self.to_openapi_dict()
        with open(file, "w+", encoding="utf-8") as f:
            safe_dump(spec_dict, f, indent=4)

    @staticmethod
    def from_openapi_file(file: str, name: str) -> RemoteToolkit:
        """only support openapi v3.0.1

        Args:
            file (str): the path of openapi yaml file
        """
        from openapi_spec_validator import validate
        from openapi_spec_validator.readers import read_from_filename

        spec_dict, _ = read_from_filename(file)
        validate(spec_dict)

        # info
        info = EndpointInfo(**spec_dict["info"])
        servers = [Endpoint(**server) for server in spec_dict.get("servers", [])]

        # components
        component_schemas = spec_dict["components"]["schemas"]
        fields = {}
        for schema_name, schema in component_schemas.items():
            parameter_view = ToolParameterView.from_openapi_dict(schema_name, schema)
            fields[schema_name] = parameter_view

        # paths
        paths = []
        for path, path_info in spec_dict.get("paths", {}).items():
            for method, path_method_info in path_info.items():
                paths.append(
                    RemoteToolView.from_openapi_dict(
                        uri=path,
                        method=method,
                        path_info=path_method_info,
                        parameters_views=fields,
                    )
                )

        return RemoteToolkit(
            name=name,
            openapi=spec_dict["openapi"],
            info=info,
            servers=servers,
            paths=paths,
            component_schemas=fields,
        )  # type: ignore

    def function_call_schema(self) -> List[dict]:
        schemas = []
        for tool_view in self.paths:
            schema = tool_view.function_call_schema()

            schema["name"] = f"{self.name}-{schema['name']}"
            schemas.append(schema)
        return schemas
