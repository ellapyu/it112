def test_register(client):
        response= client.post("/register", data={
                "csrf_token": "",
                "username": "testuser",
                "email": "test@email.com",
                "password": "Test@123!",
                "confirm": "Test@123!"
                }, follow_redirects = True)
        assert response.status_code == 200
        assert response.request.path == '/login'

def test_login(client):
        response = client.post('/login', data={
                "csrf_token": "",
                "login_field": "testuser",
                "password": "Test@123!"
                }, follow_redirects = True)
        assert response.status_code == 200
        assert response.request.path == '/'

def test_logout(client):
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/login'
        