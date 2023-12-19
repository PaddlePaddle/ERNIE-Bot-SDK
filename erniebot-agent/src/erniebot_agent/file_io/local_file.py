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

import pathlib
import time
import uuid
from typing import Any, Dict

import anyio

from erniebot_agent.file_io.base import File
from erniebot_agent.file_io.protocol import (
    FilePurpose,
    build_local_file_id_from_uuid,
    is_local_file_id,
)


class LocalFile(File):
    def __init__(
        self,
        *,
        id: str,
        filename: str,
        byte_size: int,
        created_at: int,
        purpose: FilePurpose,
        metadata: Dict[str, Any],
        path: pathlib.Path,
    ) -> None:
        if not is_local_file_id(id):
            raise ValueError(f"Invalid file ID: {id}")
        super().__init__(
            id=id,
            filename=filename,
            byte_size=byte_size,
            created_at=created_at,
            purpose=purpose,
            metadata=metadata,
        )
        self.path = path

    async def read_contents(self) -> bytes:
        return await anyio.Path(self.path).read_bytes()

    def _get_attrs_str(self) -> str:
        attrs_str = super()._get_attrs_str()
        attrs_str += f", path: {repr(self.path)}"
        return attrs_str


def create_local_file_from_path(
    file_path: pathlib.Path,
    file_purpose: FilePurpose,
    file_metadata: Dict[str, Any],
) -> LocalFile:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist.")
    file_id = _generate_local_file_id()
    filename = file_path.name
    byte_size = file_path.stat().st_size
    created_at = int(time.time())
    file = LocalFile(
        id=file_id,
        filename=filename,
        byte_size=byte_size,
        created_at=created_at,
        purpose=file_purpose,
        metadata=file_metadata,
        path=file_path,
    )
    return file


def _generate_local_file_id():
    return build_local_file_id_from_uuid(str(uuid.uuid1()))