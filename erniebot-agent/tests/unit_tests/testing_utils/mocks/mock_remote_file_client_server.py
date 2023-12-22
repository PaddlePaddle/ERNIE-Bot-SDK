import contextlib

from erniebot_agent.file_io import protocol
from erniebot_agent.file_io.remote_file import RemoteFile, RemoteFileClient


class FakeRemoteFileClient(RemoteFileClient):
    def __init__(self, server):
        super().__init__()
        self._server = server

    @property
    def server(self):
        if not self._server.started:
            raise RuntimeError("Server is not running.")
        return self._server

    async def upload_file(self, file_path, file_purpose, file_metadata):
        result = await self.server.upload_file(file_path, file_purpose, file_metadata)
        return self._create_file_obj_from_dict(result)

    async def retrieve_file(self, file_id):
        result = await self.server.retrieve_file(file_id)
        return self._create_file_obj_from_dict(result)

    async def retrieve_file_contents(self, file_id):
        return await self.server.retrieve_file_contents(file_id)

    async def list_files(self):
        result = await self.server.list_files()
        files = []
        for item in result:
            file = self._create_file_obj_from_dict(item)
            files.append(file)
        return files

    async def delete_file(self, file_id) -> None:
        await self.server.delete_file(file_id)

    async def create_temporary_url(self, file_id, expire_after):
        raise RuntimeError("Method not supported")

    def _create_file_obj_from_dict(self, dict_):
        return RemoteFile(
            id=dict_["id"],
            filename=dict_["filename"],
            byte_size=dict_["byte_size"],
            created_at=dict_["created_at"],
            purpose=dict_["purpose"],
            metadata=dict_["metadata"],
            client=self,
        )


class FakeRemoteFileServer(object):
    def __init__(self):
        super().__init__()
        self._storage = None
        self._file_id_iter = protocol.generate_fake_remote_file_ids()

    @property
    def storage(self):
        return self._storage

    @property
    def started(self):
        return self._storage is not None

    async def upload_file(self, file_path, file_purpose, file_metadata):
        id_ = next(self._file_id_iter)
        filename = file_path.name
        byte_size = file_path.stat().st_size
        created_at = protocol.get_timestamp()
        with file_path.open("rb") as f:
            contents = f.read()
        file = dict(
            id=id_,
            filename=filename,
            byte_size=byte_size,
            created_at=created_at,
            purpose=file_purpose,
            metadata=file_metadata,
            contents=contents,
        )
        self._storage[id_] = file
        return file

    async def retrieve_file(self, file_id):
        try:
            return self._storage[file_id]
        except KeyError as e:
            raise ServerError("File not found") from e

    async def retrieve_file_contents(self, file_id):
        try:
            file = self._storage[file_id]
        except KeyError as e:
            raise ServerError("File not found") from e
        else:
            return file["contents"]

    async def list_files(self):
        return list(self._storage.values())

    async def delete_file(self, file_id) -> None:
        try:
            return self._storage[file_id]
        except KeyError as e:
            raise ServerError("File not found") from e

    @contextlib.contextmanager
    def start(self):
        self._storage = {}
        yield self
        self._storage = None


class ServerError(Exception):
    pass
