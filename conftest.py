import pytest
from main import app, db_session
from data.users import User
from data.characters import Character


@pytest.fixture
def client():
    """Создает тестовый клиент Flask"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    if not hasattr(db_session, '_factory_initialized'):
        db_session.global_init('db/test_busyness.db')
        db_session._factory_initialized = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def auth(client):
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def register(self, username='testuser', email='test@example.com', password='password123'):
            return self._client.post('/register', data={
                'login': username,
                'email': email,
                'password': password,
                'repeat_password': password
            }, follow_redirects=True)

        def login(self, username='testuser', password='password123'):
            return self._client.post('/login', data={
                'login': username,
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return self._client.get('/logout', follow_redirects=True)

    return AuthActions(client)


@pytest.fixture(autouse=True)
def clean_db(request):
    yield
    sess = db_session.create_session()
    try:
        sess.query(Character).delete()
        sess.query(User).delete()
        sess.commit()
    finally:
        sess.close()