from importlib.resources import files

GRAPHQL_FILES_PATH = "data_platform_catalogue.client.graphql"
GRAPHQL_FILE_EXTENSION = ".graphql"


def get_graphql_query(graphql_query_file_name: str) -> str:
    query_text = (
        files(GRAPHQL_FILES_PATH)
        .joinpath(f"{graphql_query_file_name}{GRAPHQL_FILE_EXTENSION}")
        .read_text()
    )
    return query_text
