import pytest
import json


class TestMainRoutes:
    def test_index_loads_for_guest(self, client):
        """Главная страница должна загружаться для гостя (лендинг)"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'login' in response.data.lower()

    def test_login_page_loads(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert 'Вход'.encode('utf-8') in response.data or 'Авторизация'.encode('utf-8') in response.data

    def test_register_page_loads(self, client):
        response = client.get('/register')
        assert response.status_code == 200
        assert 'Регистрация'.encode('utf-8') in response.data


class TestAuth:
    def test_register_success(self, auth):
        response = auth.register()
        assert response.status_code == 200

    def test_login_success(self, auth, client):
        auth.register()
        response = auth.login()
        assert response.status_code == 200
        assert b'testuser' in response.data

    def test_logout(self, auth):
        auth.register()
        auth.login()
        response = auth.logout()
        assert response.status_code == 200
        assert 'Войти'.encode('utf-8') in response.data or b'login' in response.data.lower()


class TestCharacters:
    def test_create_character_requires_login(self, client):
        """Создание персонажа недоступно без входа"""
        response = client.post('/create', data={'char_name': 'Hero'}, follow_redirects=True)
        assert response.status_code == 200
        assert 'login' in str(response.request.url).lower() or 'Авторизация'.encode('utf-8') in response.data

    def test_create_character_success(self, auth, client):
        auth.register()
        auth.login()

        response = client.post('/create', data={
            'char_name': 'Test Hero',
            'race': 'Human',
            'class_level': 'Fighter 1',
            'str_score': 15,
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Test Hero' in response.data

    def test_api_characters_protected(self, client):
        response = client.get('/api/characters')
        assert response.status_code == 302

    def test_api_characters_returns_json(self, auth, client):
        auth.register()
        auth.login()
        client.post('/create', data={'char_name': 'Api Hero'})

        response = client.get('/api/characters')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]['char_name'] == 'Api Hero'


class TestDndApi:
    def test_dnd_races_api_status(self, client):
        try:
            response = client.get('/api/dnd/races')
            assert response.status_code in [200, 502]
        except Exception:
            pytest.skip("Нет интернета")