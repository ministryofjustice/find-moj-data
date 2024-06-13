from data_platform_catalogue.search_types import ResultType


def filter_seleted_domains(domain_list, domains):
    selected_domain = {}
    for domain in domain_list:
        if domain.value in domains:
            selected_domain[domain.value] = domain.label
    return selected_domain


def get_domain_list(client):
    facets = client.search_facets(
        results_types=[ResultType.TABLE, ResultType.CHART, ResultType.DATABASE]
    )
    domain_list = facets.options("domain")
    return domain_list
