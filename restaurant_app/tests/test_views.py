from rest_framework.test import APIClient
from rest_framework import status
from restaurant_app.models import FoodItem
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile 
from PIL import Image
import io
from django.contrib.auth import get_user_model

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def food_item_data():
    # Create a small image in memory
    image = Image.new('RGB', (100, 100), color='blue')
    image_file = io.BytesIO()
    image.save(image_file, format='JPEG')
    image_file.seek(0) 

    return {
        "name": "Pizza",
        "description": "Delicious cheese pizza",
        "price": 10.99,
        "category": "Italian",
        "image": SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")
    }


@pytest.mark.django_db
def test_register_user(client):
    user_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "password123"
    }
    response = client.post('/api/register/', user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == user_data['username']

@pytest.mark.django_db
def test_get_food_items(client):
    # Get the user model dynamically
    User = get_user_model()

    # Create a test user
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }
    user = User.objects.create_user(**user_data)

    client.force_authenticate(user=user)

    # Create a food item
    food_item = FoodItem.objects.create(
        name="Burger",
        description="Cheesy burger",
        price=8.99,
        category="American"
    )

    # Make the GET request
    response = client.get('/api/food-items/')
    
    # Assert response
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0

