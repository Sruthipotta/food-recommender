import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db  
def test_register_url(client):
    url = reverse('register') 
    response = client.post(url, {"username": "test", "email": "test@example.com", "password": "password"})
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db  
def test_login_url(client):
    # Create the user first, as login needs the user to be present in the database
    # Ensure the user is created before attempting to log in
    url_register = reverse('register')  
    client.post(url_register, {"username": "test", "email": "test@example.com", "password": "password"})
    
    url_login = reverse('token_obtain_pair')
    response = client.post(url_login, {"username": "test", "password": "password"})
    assert response.status_code == status.HTTP_200_OK
