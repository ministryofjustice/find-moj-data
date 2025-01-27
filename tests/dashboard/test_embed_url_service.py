from unittest import mock

from botocore.exceptions import ClientError

from dashboard.service import generate_embed_url_for_anonymous_user


@mock.patch("dashboard.service.get_quicksight_client")
def test_generateEmbedUrlForAnonymousUser_success(mock_get_quicksight_client):
    mock_quicksight_client = mock.Mock()
    mock_get_quicksight_client.return_value = mock_quicksight_client
    mock_quicksight_client.generate_embed_url_for_anonymous_user.return_value = {
        "EmbedUrl": "https://example.com/embed_url"
    }

    embed_url = generate_embed_url_for_anonymous_user()

    mock_get_quicksight_client.assert_called_once()

    assert embed_url == "https://example.com/embed_url"


@mock.patch("dashboard.service.get_quicksight_client")
def test_generateEmbedUrlForAnonymousUser_failure(mock_get_quicksight_client):
    mock_quicksight_client = mock.Mock()
    mock_get_quicksight_client.return_value = mock_quicksight_client
    mock_quicksight_client.generate_embed_url_for_anonymous_user.side_effect = (
        ClientError(
            {"Error": {"Code": "500", "Message": "Internal Server Error"}},
            "GenerateEmbedUrl",
        )
    )

    embed_url = generate_embed_url_for_anonymous_user()

    mock_get_quicksight_client.assert_called_once()

    assert embed_url is None
