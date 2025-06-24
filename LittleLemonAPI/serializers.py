from rest_framework import serializers
from .models import MenuItem, Cart, Category, Order, OrderItem
from django.contrib.auth.models import User
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','slug','title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']

    def create(self, validated_data):
        category_id = self.validated_data['category_id']
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:

            raise serializers.ValidationError({"category_id": "Category not found."})
        
        menuItem = MenuItem.objects.create(category= category, **validated_data)
        return menuItem
    
class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset = MenuItem.objects.all(),write_only=True,source='menuitem'
    )
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menu_item_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price','price']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']


        
class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset = Order.objects.all(),
        
        source = "order"
    )

    menuitem = MenuItemSerializer(read_only=True)
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset = MenuItem.objects.all(),write_only=True,source='menuitem'
    )

    class Meta:
        model = OrderItem
        fields = ['id','order_id','menuitem','menu_item_id','quantity','unit_price','price']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.filter(groups__name='Delivery-crew'),
        write_only = True,
        source = 'delivery_crew'
    )
    order_items = OrderItemSerializer(read_only=True,many=True)
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew_id','delivery_crew','order_items','status','total','date']


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request is None  or not request.user.groups.filter(name='Manager').exists():
            # si l'utilisateur n'est pas manager, on supprime 'user' des champs exposés
            fields.pop('user', None)

        return fields

        