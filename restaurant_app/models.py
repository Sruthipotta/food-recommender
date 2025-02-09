from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import process_image


def food_image_upload_path(instance, filename):
    """Generate file path for food images."""
    ext = filename.split('.')[-1]
    return f'food_items/{instance.name}_{instance.id}.{ext}'


def profile_picture_upload_path(instance, filename):
    """Generate file path for profile pictures."""
    ext = filename.split('.')[-1]
    return f'profile_pictures/{instance.username}_{instance.id}.{ext}'


class User(AbstractUser):
    ADMIN = 'admin'
    CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CUSTOMER, 'Customer'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.profile_picture:
            # Process the profile picture before saving
            processed_image = process_image(self.profile_picture)
            self.profile_picture.save(
                self.profile_picture.name,  # Use the same filename
                processed_image,  # Pass the processed image
                save=False  # Avoid saving the model again
            )
        super().save(*args, **kwargs)


class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to=food_image_upload_path)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.image:
            # Process food image before saving
            processed_food_image = process_image(self.image)
            self.image.save(
                self.image.name,  # Use the same filename
                processed_food_image,  # Pass the processed image
                save=False  # Avoid saving the model again
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(FoodItem, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
