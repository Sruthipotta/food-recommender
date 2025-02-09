from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count
from sklearn.preprocessing import StandardScaler
import numpy as np
from .utils import process_image
from .recommender import RestaurantRecommender

from .models import User, FoodItem, Order, OrderItem
from .serializers import UserSerializer, FoodItemSerializer, OrderSerializer
from .permissions import IsAdmin, IsCustomer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(role='customer')

        profile_picture = self.request.FILES.get('profile_picture')
        if profile_picture:
            user.profile_picture = profile_picture
            processed_image = process_image(profile_picture)
            user.profile_picture.save(user.profile_picture.name, processed_image, save=True)
        
        user.save()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsAdmin]
        elif self.action == 'create':
            permission_classes = [IsCustomer]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class RecommendationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        recommender = RestaurantRecommender(
            user=self.request.user, 
            Order=Order, 
            OrderItem=OrderItem, 
            FoodItem=FoodItem
        )
        
        recommended_food_ids = recommender.get_recommendations()
        return FoodItem.objects.filter(id__in=recommended_food_ids)