import os
import tempfile
import pytest

from flask import app


@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    client = app.app.test_client()

    with app.app.app_context():
        app.init_db()

    yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])

def test_empty_db(client):
    """Start with a blank database."""
    
    rv = client.get("/")
    assert b'test root' in rv.data
