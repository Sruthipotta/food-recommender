import pytest
from django.contrib.auth import get_user_model
from restaurant_app.models import FoodItem, OrderItem, Order
from restaurant_app.recommender import RestaurantRecommender

# Fixture for creating a test user
@pytest.fixture
@pytest.mark.django_db
def user():
    User = get_user_model()
    return User.objects.create_user(username="testuser", email="test@example.com", password="password123")

# Fixture for creating a food item
@pytest.fixture
@pytest.mark.django_db
def food_item():
    return FoodItem.objects.create(name="Pizza", description="Delicious pizza", price=10.99)

@pytest.fixture
@pytest.mark.django_db
def order_data(user, food_item):
    # Create the order
    order = Order.objects.create(customer=user, total_price=food_item.price)  # Assuming total price = food item price
    # Create the OrderItem and set the price field
    OrderItem.objects.create(order=order, food_item=food_item, quantity=1, price=food_item.price)
    return order


@pytest.fixture
@pytest.mark.django_db
def recommender(user, food_item):
    # Create an order with food items for the user
    order = Order.objects.create(customer=user, total_price=food_item.price, status='completed')
    OrderItem.objects.create(order=order, food_item=food_item, quantity=1, price=food_item.price)
    return RestaurantRecommender(user=user, Order=Order, OrderItem=OrderItem, FoodItem=FoodItem)

@pytest.mark.django_db  # Ensure that the test has database access
def test_collaborative_filtering(recommender):
    # Get the User model dynamically
    User = get_user_model()

    # Create users
    user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
    user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")
    
    # Create food items
    food_item1 = FoodItem.objects.create(name="Pizza", description="Delicious cheese pizza", price=10.99)
    food_item2 = FoodItem.objects.create(name="Burger", description="Juicy beef burger", price=8.99)
    food_item3 = FoodItem.objects.create(name="Pasta", description="Creamy pasta", price=12.99)

    # Create orders for users
    order1 = Order.objects.create(customer=user1, total_price=food_item1.price, status="completed")
    OrderItem.objects.create(order=order1, food_item=food_item1, quantity=1, price=food_item1.price)

    order2 = Order.objects.create(customer=user2, total_price=food_item2.price, status="completed")
    OrderItem.objects.create(order=order2, food_item=food_item2, quantity=1, price=food_item2.price)
    
    order3 = Order.objects.create(customer=user2, total_price=food_item3.price, status="completed")
    OrderItem.objects.create(order=order3, food_item=food_item3, quantity=1, price=food_item3.price)

    # Now try to get recommendations
    recommendations = recommender.collaborative_filtering()
    
    print(f"Collaborative filtering recommendations: {recommendations}")
    
    # Ensure the recommendations are not empty
    assert isinstance(recommendations, list), "Recommendations should be a list."
    assert len(recommendations) > 0, "Recommendations should not be empty."



# Test for content-based filtering
@pytest.mark.django_db
def test_content_based_filtering(recommender):
    recommendations = recommender.content_based_filtering()
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

# Test for popularity-based recommendations
@pytest.mark.django_db
def test_popularity_based(recommender):
    recommendations = recommender.popularity_based()
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
