
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='home'),
    path('item/<id>/', views.ProductDetailView.as_view(), name='detail'),
    path('buy/<id>/', views.create_checkout_session, name='api_checkout_session'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('failed/', views.PaymentFailedView.as_view(), name='failed'),
    path('create-checkout-session/<pk>', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('create-payment-intent/<pk>/', views.StripeIntentView.as_view(), name='create-payment-intent'),
    
    path('cart', views.OrderListView.as_view(), name='order'),
    path('add_to_cart/<id>/', views.add_to_cart, name='add')
]
