from rest_framework.exceptions import ValidationError
from restaurant_app.serializers import UserSerializer, FoodItemSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

@pytest.fixture
@pytest.mark.django_db  # This marks the fixture as needing database access
def user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password",
    }

@pytest.fixture
@pytest.mark.django_db  # This marks the fixture as needing database access
def food_item_data():
    # Create a small image in memory
    image = Image.new('RGB', (100, 100), color='blue')  # Create a blue image (100x100 pixels)
    image_file = io.BytesIO()
    image.save(image_file, format='JPEG')
    image_file.seek(0)  # Reset pointer to the start of the image
    return {
        "name": "Pizza",
        "description": "Delicious cheese pizza",
        "price": 10.99,
        "category": "Italian",
        "image": SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")
    }

@pytest.mark.django_db  # Marking the test function for database access
def test_user_serializer_create(user_data):
    serializer = UserSerializer(data=user_data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]

@pytest.mark.django_db  # Marking the test function for database access
def test_food_item_serializer_create(food_item_data):
    serializer = FoodItemSerializer(data=food_item_data)
    assert serializer.is_valid()
    food_item = serializer.save()
    assert food_item.name == food_item_data["name"]
