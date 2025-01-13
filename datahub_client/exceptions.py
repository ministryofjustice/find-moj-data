class CatalogueError(Exception):
    """
    Base class for catalogue-related errors.
    """


class ConnectivityError(CatalogueError):
    """
    Unable to collect to the Datahub catalog
    """


class MissingDatabaseMetadata(Exception):
    """"""


class EntityDoesNotExist(CatalogueError):
    """"""


class AspectDoesNotExist(CatalogueError):
    """"""
