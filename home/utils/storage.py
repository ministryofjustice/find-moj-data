from typing import Any
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

class NonstrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.manifest_strict = False
