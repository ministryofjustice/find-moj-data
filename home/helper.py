def filter_seleted_domains(domain_list, domains):
    selected_domain = {}
    for domain in domain_list:
        if domain.value in domains:
            selected_domain[domain.value] = domain.label
    return selected_domain


def set_search_page_contexts(total_pages: int, current_page: str, context: dict):
    """
    helper function to set context variables to be used in the pagination template
    """

    if current_page is None:
        current_page = "0"
    mid_pages_shown = 5
    mid_start_page = (
        int(current_page) - 1 if int(current_page) + 1 > 3 else int(current_page) + 1
    )
    mid_end_page = (
        int(current_page) + mid_pages_shown - 1
        if int(current_page) + 1 < total_pages
        else total_pages + 1
    )
    # a fresh search where no page has been selected
    if int(current_page) == 0:
        context["current_page"] = 1
        context["show_pages"] = [str(i) for i in range(2, mid_pages_shown + 2)]
    else:
        context["current_page"] = int(current_page) + 1
        context["show_pages"] = [str(i) for i in range(mid_start_page, mid_end_page)]

    # Here we want to display every page
    if total_pages <= 6:
        context["show_pages"] = [str(i) for i in range(2, total_pages + 1)]
    elif int(current_page) + 1 < 7:
        context["show_pages"] = [str(i) for i in range(2, mid_pages_shown + 2)]

    context["last_page_str"] = str(total_pages)
    context["last_page"] = total_pages
    context["no_ellipses_end"] = total_pages - 4
    context["current_page_str"] = str(context["current_page"])
    context["previous_page"] = str(context["current_page"] - 1)
    context["next_page"] = str(context["current_page"] + 1)

    return context
