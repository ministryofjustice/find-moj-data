def filter_seleted_domains(domain_list, domains):
    selected_domain = {}
    for domain in domain_list:
        if domain.value in domains:
            selected_domain[domain.value] = domain.label
    return selected_domain