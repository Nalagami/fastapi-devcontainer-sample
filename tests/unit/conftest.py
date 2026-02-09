"""Unit test configuration."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def setup_unit_test_db(test_db_session, monkeypatch) -> None:
    """Set up test database for unit tests."""
    import app.models.base
    import app.crud.task

    # Replace SessionLocal with test_db_session
    mock_session_local = MagicMock(return_value=test_db_session)
    monkeypatch.setattr(app.models.base, "SessionLocal", mock_session_local)
    monkeypatch.setattr(app.crud.task, "SessionLocal", mock_session_local)
