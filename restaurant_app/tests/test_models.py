import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from restaurant_app.models import FoodItem
from PIL import Image
import io

@pytest.fixture
@pytest.mark.django_db 
def user():
    return get_user_model().objects.create_user(username='testuser', email='test@example.com', password='password')


@pytest.fixture
@pytest.mark.django_db 
def food_item():
    image = Image.new('RGB', (100, 100), color='blue')  
    image_file = io.BytesIO()
    image.save(image_file, format='JPEG')
    image_file.seek(0) 

    return FoodItem.objects.create(
        name="Pizza",
        description="Delicious cheese pizza",
        price=10.99,
        category="Italian",
        image=SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")
    )


@pytest.mark.django_db 
def test_user_save(user):
    user.save()
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'

@pytest.mark.django_db
def test_food_item_save(food_item):
    food_item.save()
    assert food_item.image is not None
