from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

class NonstrictManifestStaticFilesStorage(ManifestStaticFilesStorage):
    manifest_strict = False
