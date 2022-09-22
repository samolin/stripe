from urllib import request
import stripe
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from .models import Item
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
from .models import Order, Order_Product
from django.views.generic import ListView, DetailView
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect


stripe.api_key = settings.STRIPE_SECRET_KEY

class ProductListView(ListView):
    model = Item
    template_name = "payment_service/product_list.html"
    context_object_name = 'product_list'

    def get_context_data(self, **kwargs):
        create_session(self.request)
        return super(ProductListView, self).get_context_data(**kwargs)

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
    main_domain = settings.MAIN_DOMAIN
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
            order = Order.objects.get(session_id=request.session['session_id'])
        except:
            Order.objects.create(session_id=request.session['session_id'])
            order = Order.objects.get(session_id=request.session['session_id'])
        Order_Product.objects.create(cart_id = order, item_id = Item.objects.get(id=id))
        return redirect('home')

class OrderListView(ListView):
    model = Order
    template_name = "payment_service/cart_list.html"
    
    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        try: 
            context['cart_id'] = Order.objects.get(session_id=self.request.session['session_id']).id
            context['cart_list'] = Order_Product.objects.filter(cart_id=context['cart_id'])
            return context
        except:
            return context

@csrf_exempt
def create_checkout_session_order(request, id):
    main_domain = settings.MAIN_DOMAIN
    order_id = Order_Product.objects.filter(cart_id = id)
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
    current_order.status = 'finished'
    current_order.save()
    return (JsonResponse({'sessionId': checkout_session.id}))

def create_session(request):
    try:
        return request.session['session_id']
    except: 
        request.session.create()
        request.session['session_id'] = request.session.session_key
        return request.session['session_id']
