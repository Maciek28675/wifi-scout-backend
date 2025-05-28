# from fastapi.testclient import TestClient
# from app.main import app
# from app.models.post import Post
# from app.schemas.post import PostCreate, PostUpdate

# client = TestClient(app)

# def test_create_post():
#     response = client.post("/posts/", json={"title": "Test Post", "content": "This is a test post."})
#     assert response.status_code == 201
#     assert response.json()["title"] == "Test Post"

# def test_read_post():
#     response = client.get("/posts/1")
#     assert response.status_code == 200
#     assert response.json()["id"] == 1

# def test_update_post():
#     response = client.put("/posts/1", json={"title": "Updated Post", "content": "This is an updated test post."})
#     assert response.status_code == 200
#     assert response.json()["title"] == "Updated Post"

# def test_delete_post():
#     response = client.delete("/posts/1")
#     assert response.status_code == 204

# def test_read_nonexistent_post():
#     response = client.get("/posts/999")
#     assert response.status_code == 404