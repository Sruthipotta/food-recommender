import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from restaurant_app.models import FoodItem
from PIL import Image
import io

@pytest.fixture
@pytest.mark.django_db  # This marks the fixture as needing database access
def user():
    return get_user_model().objects.create_user(username='testuser', email='test@example.com', password='password')


@pytest.fixture
@pytest.mark.django_db  # This marks the fixture as needing database access
def food_item():
    # Create a small image in memory
    image = Image.new('RGB', (100, 100), color='blue')  # Create a blue image (100x100 pixels)
    image_file = io.BytesIO()
    image.save(image_file, format='JPEG')
    image_file.seek(0)  # Reset pointer to the start of the image

    return FoodItem.objects.create(
        name="Pizza",
        description="Delicious cheese pizza",
        price=10.99,
        category="Italian",
        image=SimpleUploadedFile("test_image.jpg", image_file.read(), content_type="image/jpeg")
    )

# def test_user_save(user):
#     user.save()
#     assert user.profile_picture is not None

@pytest.mark.django_db  # Mark the test that interacts with the database
def test_user_save(user):
    user.save()
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'

@pytest.mark.django_db
def test_food_item_save(food_item):
    food_item.save()
    assert food_item.image is not None
