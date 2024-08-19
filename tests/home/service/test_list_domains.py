import pytest


class TestListDomains:
    @pytest.mark.parametrize("filter_zero_entities", [False])
    def test_list_all_domains(self, mock_catalogue, list_domains):
        domains = list_domains
        assert len(domains) == 4

    @pytest.mark.parametrize("filter_zero_entities", [True])
    def test_list_domains_exclude_zero_entities(self, mock_catalogue, list_domains):
        domains = list_domains
        assert len(domains) == 3
        assert all(domain.total > 0 for domain in domains)
