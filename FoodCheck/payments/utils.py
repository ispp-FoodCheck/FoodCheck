from django.conf import settings
import datetime
import stripe

stripe.api_key = settings.STRIPE_API_KEY

def es_premium(user):
   
    if user.premiumHasta and user.premiumHasta >= datetime.datetime.now().date():
        return True
    if not user.subscription:
        return False
    subscriptions = stripe.Subscription.list(limit=1, customer=user.subscription, price=settings.STRIPE_PRICE_ID)
    if len(subscriptions.data) == 0 or not subscriptions.data[0].plan.active:
        return False
    user.premiumHasta = datetime.datetime.fromtimestamp(subscriptions.data[0].current_period_end)
    user.save()
    return True
