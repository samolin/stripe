import json
from urllib import request
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from .models import Item
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
import stripe
from .models import Order, Order_Product


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

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(id=item_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': item.price,
                        'product_data': {
                            'name': item.name,
                            # 'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": item.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id 
        })

class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            item_id = self.kwargs["pk"]
            item = Item.objects.get(id=item_id)
            intent = stripe.PaymentIntent.create(
                amount=item.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": item.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })

from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http.response import HttpResponseNotFound
from django.shortcuts import redirect

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
        request.session['product'] = [id]
        try:
            latest = Order.objects.latest('id')
            #request.session['product'] += [id]
            if latest and latest.status == 'in_process':
                print('order_is already exist', latest.id)
        except:
            Order.objects.create()
            #latest = Order.objects.latest('id')
            print('I created it only now')
        request.session['product'] += [id]
        print(request.session['product'])
        Order_Product.objects.create(item_id = Item.objects.get(id = id),cart_id = Order.objects.latest('id'))
            #request.session['product'] = [id]
        #print(request.session['product'])
        #if latest and latest.status == 'in_process':
        #    print('order_is already exist')
        #else:
        #    Order.objects.create()
        #    print('I created it only now')
            #item = Item.objects.get(pk=id)
            #order = Order()
            #order.item = item
            #order.amount = int(item.price)
            #order.save()
        return redirect('home')



class OrderListView(ListView):
    model = Order
    template_name = "payment_service/cart_list.html"
    context_object_name = 'cart_list'

    def get_context_data(self, **kwargs):
        lts = Order.objects.latest('id')
        print(Order.objects.latest('id'))
        print(Order_Product.objects.get(id=lts))
        kwargs['cart_list'] = Order.objects.all()
        return super(OrderListView, self).get_context_data(**kwargs)

