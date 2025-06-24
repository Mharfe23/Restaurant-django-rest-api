from django.shortcuts import render
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from .serializers import MenuItemSerializer,CategorySerializer,UserSerializer,CartSerializer,OrderItemSerializer,OrderSerializer
# Create your views here.
from .permissions import isManager
from django.contrib.auth.models import User,Group
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle



@api_view()
@permission_classes([IsAuthenticated])
def test(request):
    return Response({"message":"accessed secure endpoint"})

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    filterset_fields = ['price', 'inventory']
    search_fields = ['title']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        
        return [IsAuthenticated(), isManager()]


class MenuItemViewSingle(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsAuthenticated(), isManager()]
    

class GroupView(APIView):
    permission_classes = [isManager]

    def get(self, request ,*args, **kwargs):
        # List users in Manager group
        group_name = kwargs['group_name']
        cap_group_name = group_name[0].upper() + group_name[1:]
        users = User.objects.filter(groups__name=cap_group_name)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request,*args, **kwargs):
        group_name = kwargs['group_name']
        cap_group_name = group_name[0].upper() + group_name[1:]

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error':'User Id is required'},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=cap_group_name)
            user.groups.add(group)
            return Response({'message':f'User {user.username} assigned to {cap_group_name} group'},status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error':'User Not found'},status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error':f'Group {group_name} does not exists'},status=status.HTTP_404_NOT_FOUND)
        
    
        
class GroupDeleteSingleView(APIView):

    permission_classes = [isManager]

    def delete(self, request, *args, **kwargs):
        group_name = kwargs['group_name']
        user_id = kwargs['userId']
        cap_group_name = group_name[0].upper() + group_name[1:]

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name=cap_group_name)

            user.groups.remove(group)
            return Response({'message':f'revoked {cap_group_name} from User with user id: {user_id}'},status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error':'User Not found'},status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({'error':f'Group {group_name} does not exists'},status=status.HTTP_404_NOT_FOUND)
        


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request,*args, **kwargs):
        
        serializer = CartSerializer(data= request.data)

        if serializer.is_valid():
            menu_item = serializer.validated_data['menuitem']
            quantity = serializer.validated_data['quantity']

            unit_price = menu_item.price
            
            total_price = unit_price * quantity

            serializer.save(
                user = request.user,
                unit_price= unit_price,
                price = total_price
            )
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        
        return Response(Cart.objects.filter(user=request.user).delete())
    

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    ordering_fields = ['total', 'status','date']
    filterset_fields = ['total', 'status','date']
    search_fields = ['status','date']
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self,request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            order = Order.objects.all()

        elif user.groups.filter(name="Delivery-crew"):
            order = Order.objects.filter(delivery_crew=user)

        else:
            order = Order.objects.filter(user = request.user)
        serializer = OrderSerializer(order, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self,request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items:
            return Response({"error":"Cart is empty"},status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():

            order = Order.objects.create(user=user,total=0)
            order_items = []
            total_price = 0

            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price = item.price
                )
                total_price += item.price
                order_items.append(order_item)

            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()
            order.total = total_price
            order.save()
            return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error":"Error in creating the order"},status=status.HTTP_400_BAD_REQUEST)
    
class OrderSingleView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get(self,request, *args, **kwargs):

        orderId = kwargs['orderId']

        try:
            order = Order.objects.get(id = orderId, user= request.user)

        except Order.DoesNotExist:
            return Response({"error": "You have no Order with this ID"}, status=status.HTTP_404_NOT_FOUND)

        serialized_data = OrderSerializer(order, context={'request':request})

        return Response(serialized_data.data, status=status.HTTP_200_OK)
    
    def delete(self,request, *args, **kwargs):

        orderId = kwargs['orderId']

        if request.user.groups.filter(name="Manager").exists():
            try:
                order = Order.objects.get(id=orderId)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response(order.delete())
        
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def put(self,request, *args, **kwargs):
        orderId = kwargs['orderId']
        new_status = request.data.get('status')
        delivery_crew_id = request.data.get('delivery_crew_id')
        
        try:
            order = Order.objects.get(id=orderId)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'},status=status.HTTP_404_NOT_FOUND)

        if request.user.groups.filter(name="Delivery-crew").exists():   
            if not new_status:
                return Response({'error': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST) 
            order.status = new_status
            order.save()
            return Response({'message': 'Order status updated successfully.'}, status=status.HTTP_200_OK)
        
        
        elif request.user.groups.filter(name="Manager").exists():
            
            if delivery_crew_id:

                try:
                    delivery = User.objects.get(id=delivery_crew_id, group__name = "Delivery-crew")
                except User.DoesNotExist:
                    return Response({'error': 'Delivery crew not found.'},status=status.HTTP_404_NOT_FOUND)
                
                order.delivery_crew = delivery
            
            if new_status:
                order.status = new_status
            
            order.save()
            return Response({'message': 'Order updated successfully by manager.'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'You are not authorized to perform this action.'}, status=status.HTTP_403_FORBIDDEN) 
            