from importlib.resources import files


def get_graphql_query(graphql_query_file_name: str) -> str:
    query_text = (
        files("data_platform_catalogue.client.graphql")
        .joinpath(f"{graphql_query_file_name}.graphql")
        .read_text()
    )
    return query_text
