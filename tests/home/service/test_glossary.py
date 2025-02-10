from home.service.glossary import GlossaryService


class TestGlossaryService:
    def test_get_context(self):
        glossary_context = GlossaryService()
        expected_context = {
            "h1_value": "Glossary",
            "results": [],
        }

        assert expected_context == glossary_context.context
