def test_add_inventory(client):
    response= client.post("/register", data={
            "csrf_token": "",
            "username": "testuser",
            "email": "test@email.com",
            "password": "Test@123!",
            "confirm": "Test@123!"
            }, follow_redirects = True)
    
    response = client.post('/login', data={
            "csrf_token": "",
            "login_field": "testuser",
            "password": "Test@123!"
            }, follow_redirects = True)

    # test adding item in ingredient list
    response = client.post("/add_ingredient", data={"ingredient": "apples", "quantity": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Apples" in response.data

    # test adding new item to inventory, redirect to add to ingredient
    response = client.post("/add_ingredient", data={"ingredient": "beef jerky", "quantity": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/add_inventory_item'

    response = client.post("/add_inventory_item", data={"item": "beef jerky", "category": "Pantry", "macros": "Protein", "quantity": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'

    # test adding an inventory item that already exists
    response = client.post("/add_ingredient", data={"ingredient": "beef jerky", "quantity": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"already in your inventory" in response.data