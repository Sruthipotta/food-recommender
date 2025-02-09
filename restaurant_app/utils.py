# restaurant/utils.py
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from io import BytesIO
import numpy as np
from django.core.files.base import ContentFile
from django.db import models

def process_image(image_file, max_size=(800, 800)):
    """Process uploaded images - resize if too large and optimize"""
    img = Image.open(image_file)
    
    # Convert to RGB if image is in RGBA mode (for PNG with transparency)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize the image if it exceeds the max size
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Create a buffer to save the processed image into memory
    buffer = BytesIO()
    
    # Save as JPEG (if the image is PNG or another format)
    if img.format == 'PNG':
        img = img.convert('RGB')  # Convert PNG to RGB before saving as JPEG
        img.save(buffer, format='JPEG', quality=85, optimize=True)
    else:
        img.save(buffer, format=img.format, quality=85, optimize=True)
    
    # Return the processed image as a ContentFile object
    return ContentFile(buffer.getvalue())


def generate_recommendations(user, FoodItem, OrderItem, Order):
    """Generate personalized food recommendations using collaborative filtering"""
    # Get all orders and create a user-item interaction matrix
    orders = OrderItem.objects.select_related('order', 'food_item').all()
    
    # Create a DataFrame of user-item interactions
    interactions = pd.DataFrame(list(orders.values(
        'order__customer_id',
        'food_item_id',
        'quantity'
    )))
    
    if interactions.empty:
        return FoodItem.objects.all()[:10]
    
    # Pivot table to create user-item matrix
    user_item_matrix = interactions.pivot_table(
        index='order__customer_id',
        columns='food_item_id',
        values='quantity',
        fill_value=0
    )
    
    # Normalize the data
    scaler = StandardScaler()
    normalized_matrix = scaler.fit_transform(user_item_matrix)
    
    # Calculate similarity between users
    user_similarity = cosine_similarity(normalized_matrix)
    
    # Find similar users
    if user.id not in user_item_matrix.index:
        return FoodItem.objects.order_by('?')[:10]
        
    user_index = user_item_matrix.index.get_loc(user.id)
    similar_users = user_similarity[user_index].argsort()[::-1][1:6]  # top 5 similar users
    
    # Get food items liked by similar users
    similar_user_ids = user_item_matrix.index[similar_users]
    
    recommended_items = (
        OrderItem.objects
        .filter(order__customer_id__in=similar_user_ids)
        .exclude(order__customer_id=user.id)
        .values('food_item_id')
        .annotate(count=models.Count('food_item_id'))
        .order_by('-count')
        .values_list('food_item_id', flat=True)
    )
    
    # Get user's preferred categories for diversity
    user_categories = (
        OrderItem.objects
        .filter(order__customer=user)
        .values('food_item__category')
        .annotate(count=models.Count('food_item__category'))
        .order_by('-count')
        .values_list('food_item__category', flat=True)
    )
    
    # Combine recommendations with some items from user's preferred categories
    recommended_food_items = list(FoodItem.objects.filter(
        id__in=list(recommended_items)[:7]
    ))
    
    if user_categories:
        category_items = list(FoodItem.objects.filter(
            category__in=list(user_categories)[:2]
        ).exclude(
            id__in=[item.id for item in recommended_food_items]
        )[:3])
        recommended_food_items.extend(category_items)
    
    return recommended_food_items
