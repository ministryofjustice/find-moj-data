import logging
from importlib.resources import files

from ..exceptions import CatalogueError

GRAPHQL_FILES_PATH = "datahub_client.graphql"
GRAPHQL_FILE_EXTENSION = ".graphql"

logger = logging.getLogger(__name__)


def get_graphql_query(graphql_query_file_name: str) -> str:
    query_text = (
        files(GRAPHQL_FILES_PATH)
        .joinpath(f"{graphql_query_file_name}{GRAPHQL_FILE_EXTENSION}")
        .read_text()
    )
    if not query_text:
        logger.error("No graphql query file found for %s", graphql_query_file_name)
        raise CatalogueError(
            f"No graphql query file found for {graphql_query_file_name}"
        )
    return query_text
