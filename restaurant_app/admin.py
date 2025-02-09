# restaurant/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, FoodItem, Order, OrderItem


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'date_joined', 'display_profile_picture')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.profile_picture.url
            )
        return "No picture"
    display_profile_picture.short_description = 'Profile Picture'



from django.contrib import admin
from .models import FoodItem
import csv
from django.http import HttpResponse


def export_food_items_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=food_items.csv'
    writer = csv.writer(response)
    writer.writerow(['Food Item ID', 'Name', 'Description', 'Price', 'Category', 'Is Available', 'Image URL'])
    for food_item in queryset:
        writer.writerow([
            food_item.id, food_item.name, food_item.description,
            food_item.price, food_item.category, food_item.is_available,
            food_item.image.url if food_item.image else 'No Image'
        ])
    return response


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'category', 'price', 'is_available', 'display_image', 'created_at')
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('name', 'description', 'category')
    ordering = ('category', 'name')
    list_editable = ('is_available', 'price')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price')
        }),
        ('Category & Availability', {
            'fields': ('category', 'is_available')
        }),
        ('Image', {
            'fields': ('image',)
        }),
    )

    actions = [export_food_items_to_csv]

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    display_image.short_description = 'Image'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email')
    readonly_fields = ('total_price',)
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return self.readonly_fields + ('customer', 'created_at', 'updated_at')
        return self.readonly_fields


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'food_item', 'quantity', 'price')
    list_filter = ('order__status', 'food_item__category')
    search_fields = ('order__customer__username', 'food_item__name')
    readonly_fields = ('price',)

    def has_add_permission(self, request):
        return False 
