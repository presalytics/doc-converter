from doc_converter.storage.base import FileStorageBase


class InMemoryStore(FileStorageBase):
    def __init__(self, *args, **kwargs):
        self.store = {}
        super().__init__(*args)

    def allocate_key(self):
        self.store[self.key] = b'\x00'

    def get_file(self):
        return self.store[self.key]

    def put_file(self, filepath: str) -> None:
        with open(filepath, 'rb') as f:
            self.store[self.key] = f.read()

    def clean(self) -> None:
        self.store.pop(self.key, None)
