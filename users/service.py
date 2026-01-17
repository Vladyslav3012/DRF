import logging

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from Project import settings
from users.models import Order, Payment
import stripe


YOUR_DOMAIN = 'https://else-semisolemn-meta.ngrok-free.dev'
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def stripe_session_check(order, user):
    line_items = []
    tickets = order.tickets.all()

    for ticket in tickets:
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
        expires_at=int((timezone.now() + timezone.timedelta(minutes=30)).timestamp()),
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=YOUR_DOMAIN + "/success",
        cancel_url=YOUR_DOMAIN + "/cancel",
        metadata={
            "order_id": str(order.order_id),
            "user_id": user.id,
        },
    )
    payment = Payment.objects.create(order=order,
                                     owner=user,
                                     price=sum([ticket.price for ticket in tickets]),
                                     currency=order.currency,
                                     stripe_checkout_session=check_session.id)
    logger.info(f"Create payment to order #{order.order_id}")
    return check_session, payment


def webhook_check(request):
    try:
        header = request.META["HTTP_STRIPE_SIGNATURE"]
        if not header:
            logger.error("Stpire header not found")
            return HttpResponse("Header not found", status=400)
        event = stripe.Webhook.construct_event(
            request.body,
            header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except Exception as e:
        logger.exception("Something went wrong")
        return HttpResponse(str(e), status=400)
    session = event["data"]["object"]
    session_id = session['id']
    order = Order.objects.filter(stripe_checkout_session=session_id)
    payment = Payment.objects.filter(stripe_checkout_session=session_id).first()

    if event["type"] == "checkout.session.completed":
        logger.info(f"Payment {payment.payment_id} success")
        order.update(status="Confirmed")
        payment.status_payment = "Confirmed"
        payment.payed_at = timezone.now()
        payment.save(update_fields=["status_payment", "payed_at"])
        return HttpResponse({'msg': 'Order payment success'}, status=200)

    elif event["type"] == "checkout.session.expired":
        logger.info(f"Payment #{payment.payment_id} expired")
        order.status_payment = "Canceled"
        payment.save(update_fields=["status_payment"])
        return HttpResponse({'msg': 'Order payment canceled'}, status=200)

    return HttpResponse(status=200)


def expire_session(request, order):
    if not order.stripe_checkout_session:
        logger.error(f"Order has no active checkout session {order.stripe_checkout_session}")
        return HttpResponse("Order has no active checkout session", status=400)

    try:
        stripe.checkout.Session.expire(order.stripe_checkout_session)
    except stripe.error.InvalidRequestError as e:
        logger.exception("Error")
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"msg": "Checkout session expired"}, status=200)





