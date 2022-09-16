import json
import stripe
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.views import View
from .models import Item
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
from .models import Order, Order_Product
from django.views.generic import ListView, DetailView
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect


stripe.api_key = settings.STRIPE_SECRET_KEY

class LandingPageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        item = Item.objects.get(name='glass')
        context = super(LandingPageView, self).get_context_data(**kwargs)
        context.update({
            'item': item,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
        })
        return context

class ProductListView(ListView):
    model = Item
    template_name = "payment_service/product_list.html"
    context_object_name = 'product_list'

class ProductDetailView(DetailView):
    model = Item
    template_name = "payment_service/product_detail.html"
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context
    
@csrf_exempt
def create_checkout_session(request, id):
    main_domain = "http://127.0.0.1:8000"
    product = get_object_or_404(Item, pk=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.name,
                            'images': [f'https://dummyimage.com/200x150.jpg?text={ product.name }'],
                        },
                    },
                    'quantity': 1,
            }],
            metadata={
                "product_id": product.id
            },
        mode='payment',
        success_url=main_domain + '/success' + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=main_domain + '/failed',
    )
    return (JsonResponse({'sessionId': checkout_session.id}))

class PaymentFailedView(TemplateView):
    template_name = "payment_service/payment_failed.html"

class PaymentSuccessView(TemplateView):
    template_name = "payment_service/payment_success.html"

    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        if session_id is None:
            return HttpResponseNotFound("session don't find")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        return render(request, self.template_name)

def add_to_cart(request, id):
    if request.method == 'GET':
        try:
            latest = Order.objects.get(status='in_process')
        except:
            Order.objects.create()
            latest = Order.objects.get(status='in_process')
        Order_Product.objects.create(cart_id = latest, item_id = Item.objects.get(id=id))
        return redirect('home')

class OrderListView(ListView):
    model = Order
    template_name = "payment_service/cart_list.html"
    
    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        try: 
            Order.objects.get(status = 'in_process').id
            context['cart_id'] = Order.objects.get(status = 'in_process').id
            context['cart_list'] = Order_Product.objects.filter(cart_id = Order.objects.get(status = 'in_process').id)
            return context
        except:
            return context

@csrf_exempt
def create_checkout_session_order(request, id):
    main_domain = "http://127.0.0.1:8000"
    order_id = Order_Product.objects.filter(cart_id = Order.objects.get(status = 'in_process').id)
    line_items_attrs = []
    for i in order_id:
        line_items_attrs.append(
        {
            'price_data': {
                'currency': 'usd',
                'unit_amount': i.item_id.price,
                'product_data': {
                    'name': i.item_id.name,
                    'images': [f'https://dummyimage.com/200x150.jpg?text={ i.item_id.name }'],
                },
            },
            'quantity': 1,
        })
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items_attrs,
        mode='payment',
        success_url=main_domain + '/success' + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=main_domain + '/failed',
    )
    current_order = Order.objects.get(id=id)
    print(current_order)
    current_order.status = 'finished'
    current_order.save()
    return (JsonResponse({'sessionId': checkout_session.id}))

