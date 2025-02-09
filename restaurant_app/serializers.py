from rest_framework import serializers
from .models import User, FoodItem, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'profile_picture', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.CUSTOMER)
        )

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
            
        return user


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('food_item', 'quantity', 'price')
        read_only_fields = ('price',)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = ('id', 'customer', 'items', 'total_price', 'status', 'created_at')
        read_only_fields = ('customer', 'total_price')

    def create(self, validated_data):
        items_data = validated_data.pop('orderitem_set')
        order = Order.objects.create(total_price=0, **validated_data)

        total_price = 0
        for item_data in items_data:
            food_item = item_data['food_item']
            quantity = item_data['quantity']
            price = food_item.price * quantity
            total_price += price

            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price=price
            )

        order.total_price = total_price
        order.save()
        return order