import abc


class FileStorageBase(object):

    def __init__(self, key: str, file_extension: str, *args, **kwargs):
        self.key = key
        self.file_extension = file_extension

    @abc.abstractmethod
    def put_file(self, filepath: str) -> None:
        "Reads a filepath to bytes and places it in storage"
        raise NotImplementedError

    @abc.abstractmethod
    def get_file(self) -> bytes:
        "Retrieves file bytes from storage"
        raise NotImplementedError

    @abc.abstractmethod
    def allocate_key(self):
        raise NotImplementedError

    def clean(self) -> None:
        "Cleans any temporary resources used by the Storage system (e.g. cache entries, file-system objects)"
        pass

    def get_filename(self) -> str:
        "Returns a filename to used by parent objects"
        return self.key + "." + self.file_extension
