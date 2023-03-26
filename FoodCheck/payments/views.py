from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_API_KEY

@require_GET
@login_required(login_url='authentication:login')
def checkout(request):
    session = stripe.checkout.Session.create(
        success_url='http://localhost:8000/payment_completed?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:8000/payment_completed',
        mode='subscription',
        line_items=[{
            'price': settings.STRIPE_PRICE_ID,
            'quantity': 1
        }],
    )
    return redirect(session.url)

@require_GET
@login_required(login_url='authentication:login')
def payment_completed(request):
    if request.GET.get('session_id'):
        session = stripe.checkout.Session.retrieve(request.GET.get('session_id'))
        print(session)
        user = request.user
        user.subscription = session.customer
        user.save()
    return redirect('index')

@require_GET
@login_required(login_url="authentication:login")
def portal(request):
    session = stripe.billing_portal.Session.create(
        customer=request.user.subscription,
        return_url='http://localhost:8000/home',
    )
    return redirect(session.url)
