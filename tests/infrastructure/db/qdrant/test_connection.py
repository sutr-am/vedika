import pytest
from pytest_mock import MockerFixture

from vedika.infrastructure.db.qdrant.connection import QdrantDatabaseConnector

########################
# FIXTURES
########################


@pytest.fixture(autouse=True)
def reset_singleton():
    """
    Automatically resets the singleton instance before and after each test.
    This ensures state from one test does not bleed into another.
    """
    QdrantDatabaseConnector._instance = None
    yield
    QdrantDatabaseConnector._instance = None


########################
# TESTS
########################


def test_get_client_successful_connection(mocker: MockerFixture):
    # Arrange: Use the mocker fixture to patch the QdrantClient
    mock_instance = mocker.MagicMock()
    mock_qdrant_client_class = mocker.patch(
        "vedika.infrastructure.db.qdrant.connection.QdrantClient", return_value=mock_instance
    )

    # Act: Call the method
    client = QdrantDatabaseConnector.get_client()

    # Aseert:
    mock_qdrant_client_class.assert_called_once()
    mock_instance.get_collections.assert_called_once()  # verifies the ping
    assert client == mock_instance


def test_singleton_behavior(mocker: MockerFixture):
    # Arrange Patch the client so that it doesnot make real network calls
    mock_qdrant_client_class = mocker.patch(
        "vedika.infrastructure.db.qdrant.connection.QdrantClient"
    )

    # Act: request teh client twice
    client1 = QdrantDatabaseConnector.get_client()
    client2 = QdrantDatabaseConnector.get_client()

    # Assert: Both variables should point to teh exact same object in memeory
    assert client1 is client2
    # The actual QdrantClient should only have been initialized once
    mock_qdrant_client_class.assert_called_once()


def test_get_client_connection_failure(mocker: MockerFixture):
    # Arrange: Force the mock to raise a connection error
    mocker.patch(
        "vedika.infrastructure.db.qdrant.connection.QdrantClient",
        side_effect=Exception("Connection Refused"),
    )

    # Act & Assert: Verify that the exception is caught and re-raised properly
    with pytest.raises(Exception, match="Connection Refused"):
        QdrantDatabaseConnector.get_client()


def test_close_connection(mocker: MockerFixture):
    # Arrange: Mock the client and open a connection first
    mock_instance = mocker.MagicMock()
    mocker.patch(
        "vedika.infrastructure.db.qdrant.connection.QdrantClient", return_value=mock_instance
    )

    QdrantDatabaseConnector.get_client()
    assert QdrantDatabaseConnector._instance is not None

    # Act: Close the connection
    QdrantDatabaseConnector.close()

    # Aseert
    mock_instance.close.assert_called_once()
    assert QdrantDatabaseConnector._instance is None
