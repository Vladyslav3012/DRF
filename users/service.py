from django.http import HttpResponse

from Project import settings
from users.models import Order
import stripe


YOUR_DOMAIN = 'https://else-semisolemn-meta.ngrok-free.dev'
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_session_check(order, user_id):
    line_items = []

    for ticket in order.tickets.all():
        line_items.append({
            "price_data": {
                "currency": order.currency,
                "product_data": {
                    "name": f"Ticket #{ticket.id}",
                },
                "unit_amount": int(ticket.price * 100),
            },
            "quantity": 1,
        })

    check_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=YOUR_DOMAIN + "/success",
        cancel_url=YOUR_DOMAIN + "/cancel",
        metadata={
            "order_id": str(order.order_id),
            "user_id": user_id,
        },
    )
    return check_session


def webhook_check(request):
    try:
        header = request.META["HTTP_STRIPE_SIGNATURE"]
        if not header:
            return HttpResponse(status=400)
        event = stripe.Webhook.construct_event(
            request.body,
            header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception:
        return HttpResponse(status=400)
    session = event["data"]["object"]
    session_id = session['id']
    order = Order.objects.filter(stripe_checkout_session=session_id)

    if event["type"] == "checkout.session.completed":
        order.update(status="Confirmed")
    elif event["type"] == "checkout.session.expired":
        order.update(status="Expired")

    return HttpResponse(status=200)