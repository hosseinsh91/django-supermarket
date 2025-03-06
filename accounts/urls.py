from django.urls import path

from . import views
app_name = 'accounts'
urlpatterns = [
    # products urls
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/list/', views.customer_list, name='customer_list'),
    path('customer/<int:customer_id>/', views.customer_details, name='customer_details'),
    path('customer/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/profile/', views.customer_profile, name='customer_profile')
]
