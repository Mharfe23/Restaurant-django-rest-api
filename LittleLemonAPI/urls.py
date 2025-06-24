from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/',obtain_auth_token),
    path('categories/',views.CategoryView.as_view()),
    path('users/',views.UserView.as_view()),
    path('menu-items/', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>',views.MenuItemViewSingle.as_view()),
    path('groups/<str:group_name>/users',views.GroupView.as_view()),
    path('groups/<str:group_name>/users/<int:userId>',views.GroupDeleteSingleView.as_view()),
    path('cart/menu-items/',views.CartView.as_view()),
    path('orders/',views.OrderView.as_view()),
    path('orders/<int:orderId>/',views.OrderSingleView.as_view()),
]