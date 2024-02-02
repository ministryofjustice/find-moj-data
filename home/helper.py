def filter_seleted_domains(domain_list, domains):
    selected_domain = {}
    for domain in domain_list:
        if domain.value in domains:
            selected_domain[domain.value] = domain.label
    return selected_domain

def get_domain_list(client):
    facets = client.search_facets()
    domain_list = facets.options("domains")
    return domain_list
