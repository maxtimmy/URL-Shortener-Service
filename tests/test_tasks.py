from unittest.mock import MagicMock, patch
from app.tasks import cleanup_expired_links

@patch("app.tasks.SessionLocal")
def test_cleanup_expired_links_with_rows(mock_session_local):
    db = MagicMock()
    mock_session_local.return_value = db

    expired_link = MagicMock()
    unused_link = MagicMock()

    q1 = MagicMock()
    q2 = MagicMock()

    db.query.side_effect = [q1, q2]

    q1.filter.return_value.all.return_value = [expired_link]
    q2.filter.return_value.all.return_value = [unused_link]

    cleanup_expired_links()

    assert db.add.called
    assert db.delete.called
    assert db.commit.called
    assert db.close.called


@patch("app.tasks.SessionLocal")
def test_cleanup_expired_links_runs(mock_session_local):
    db = MagicMock()
    mock_session_local.return_value = db

    q1 = MagicMock()
    q2 = MagicMock()

    db.query.side_effect = [q1, q2]

    q1.filter.return_value.all.return_value = []
    q2.filter.return_value.all.return_value = []

    cleanup_expired_links()

    assert db.commit.called
    assert db.close.called