import logging
from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.db import transaction, models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from Project import settings
import stripe
from django.utils import timezone

from users.models import CustomUser
from .models import Payment, Order
from .tasks import send_email_order_task

logger = logging.getLogger(__name__)

YOUR_DOMAIN = settings.NGROK_DOMAIN
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_session_check(order, user):
    line_items = []
    tickets = order.tickets.all()
    full_price = sum([ticket.price for ticket in tickets])
    order_id = order.order_id

    payment = order.payments.order_by("-created_at").first()

    if (payment and payment.stripe_checkout_session
            and payment.session_expires_at
            and payment.session_expires_at > timezone.now()):
        session = stripe.checkout.Session.retrieve(payment.stripe_checkout_session)
        logger.info(f"Select exists active payment #{payment.payment_id} to this order")
        return session, payment

    elif not payment:
        payment = Payment.objects.create(order=order,
                                     owner=user,
                                     price=full_price,
                                     currency=order.currency)
        logger.info(f"Create new payment #{payment.payment_id} to order")
    else:
        logger.info(f"Payment exists but session expired/missing; "
                    f"create new session for payment #{payment.payment_id}")

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
        expires_at=int((timezone.now() + timezone.timedelta(minutes=31)).timestamp()),
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=YOUR_DOMAIN + "/success",
        cancel_url=YOUR_DOMAIN + "/cancel",
        metadata={
            "order_id": str(order_id),
            "payment_id": str(payment.payment_id),
            "user_id": str(user.id),
        },
    )

    payment.stripe_checkout_session = check_session.id
    payment.checkout_url = check_session.url
    payment.session_expires_at = datetime.fromtimestamp(check_session.expires_at, tz=timezone.UTC)
    payment.save(update_fields=["stripe_checkout_session", "checkout_url",
                                "session_expires_at"])

    order.stripe_checkout_session = check_session.id
    order.save(update_fields=["stripe_checkout_session"])
    seat_list = [(f"Flight {ticket.flight}. Ticket №{ticket.seat_number} "
                  f"({ticket.ticket_class} class)") for ticket in tickets]
    context = {
        'username': user.username,
        'order_id': order_id,
        'payment_id': payment.payment_id,
        'seats': seat_list,
        'full_price': full_price,
        'currency': order.currency,
        'payment_url': check_session.url
    }
    html_content = render_to_string('payment_order.html', context)
    text_content = strip_tags(html_content)
    subject = f"You payment to order {order_id}"
    email = [user.email]
    send_email_order_task.delay_on_commit(subject, text_content, html_content, email)
    return check_session, payment


def webhook_check(request, token):
    try:
        header = request.META.get("HTTP_STRIPE_SIGNATURE")
        if not header:
            logger.error("Stpire header not found")
            return HttpResponse("Header not found", status=400)
        if token != settings.SECRET_TOKEN_TO_WEBHOOK:
            return HttpResponse("Send correct secret token", status=403)

        event = stripe.Webhook.construct_event(
            request.body,
            header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    session = event["data"]["object"]
    session_id = session["id"]

    customer_detail = session.get('customer_details', {})
    email_stripe = customer_detail.get('email')

    meta = session.get("metadata", {})
    order_id = meta.get("order_id")
    payment_id = meta.get("payment_id")

    if not order_id or not payment_id or not session_id:
        logger.warning(f"Webhook missing metadata: order_id={order_id},"
                       f" payment_id={payment_id}, session_id={session_id}")
        return HttpResponse(status=200)

    payment = Payment.objects.filter(payment_id=payment_id,
                                     stripe_checkout_session=session_id).first()
    if not payment:
        logger.warning(f"Payment not found: payment_id={payment_id}")
        return HttpResponse(status=200)

    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        updated = Order.objects.filter(order_id=order_id,
                             stripe_checkout_session=session_id).update(status="Confirmed")
        payment.status_payment = "Confirmed"
        payment.payed_at = timezone.now()
        payment.save(update_fields=["status_payment", "payed_at"])

        email_db = payment.owner.email
        list_email = [email_db]
        if email_stripe != email_db:
            list_email.append(email_stripe)

        context = {
            'username': payment.owner,
            'order_id': order_id,
            'payment_id': payment.payment_id,
            'full_price': payment.price,
            'currency': payment.currency,
            'payed_at': payment.payed_at
        }
        html_content = render_to_string('payment_order_completed.html', context)
        text_content = strip_tags(html_content)
        subject = f"Payment to order #{order_id} success"

        send_email_order_task.delay_on_commit(subject, text_content, html_content, list_email)

        logger.info(f"Payment {payment.payment_id} success, order_updated={updated}")

        return JsonResponse({'msg': 'Order payment success'}, status=200)

    if event_type == "checkout.session.expired":
        updated = Order.objects.filter(
            order_id=order_id,
            stripe_checkout_session=session_id
        ).update(status="Expired")

        payment.status_payment = "Canceled"
        payment.save(update_fields=["status_payment"])

        with transaction.atomic():
            order = get_object_or_404(Order, order_id=order_id)
            tickets = order.tickets.select_related('flight')

            for ticket in tickets:
                flight = ticket.flight
                if ticket.ticket_class == 'economy':
                    flight.tickets_count_economy = models.F('tickets_count_economy') + 1
                    flight.save(update_fields=['tickets_count_economy'])
                    logger.info(f"Cancel booking #{ticket.id} (economy)")
                elif ticket.ticket_class == 'business':
                    flight.tickets_count_business = models.F('tickets_count_business') + 1
                    flight.save(update_fields=['tickets_count_business'])
                    logger.info(f"Cancel booking #{ticket.id} (business)")
                elif ticket.ticket_class == 'first':
                    flight.tickets_count_first = models.F('tickets_count_first') + 1
                    flight.save(update_fields=['tickets_count_first'])
                    logger.info(f"Cancel booking #{ticket.id} (first)")

            tickets.delete()

        logger.info(f"Payment {payment.payment_id} expired, order_updated={updated}")
        return JsonResponse({"msg": "Order payment canceled"}, status=200)

    return HttpResponse(status=200)


def expire_session(request, order):
    if not order.stripe_checkout_session:
        logger.error(f"Order has no active checkout session {order.stripe_checkout_session}")
        return JsonResponse("Order has no active checkout session", status=400)

    try:
        stripe.checkout.Session.expire(order.stripe_checkout_session)
    except stripe.error.InvalidRequestError as e:
        logger.exception(f"Error: {e}")
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"msg": "Checkout session expired"}, status=200)


def generate_payment_link(order_id: str, user_id: int) -> str:
    """
        Generates a Stripe payment link for a specific order.
        Use this tool when the user confirms they want to pay for an order.

        Args:
            order_id: The unique ID (UUID string) of the order to pay for.
            user_id: The ID of the current user.

        Returns:
            str: The payment URL (e.g., https://checkout.stripe.com/...) or an error message.
    """

    user = get_object_or_404(CustomUser, id=user_id)
    try:
        order = Order.objects.prefetch_related(
            "tickets",
            "payments"
        ).get(order_id=order_id, owner=user)
    except Exception as e:
        logger.exception(f"Order #{order_id} not found, or you are not its owner,"
                         f" error {e}")
        return "Order not found"

    status_order = ("Confirmed", "Expired")
    if order.status in status_order:
        logger.error(f"This order has already been paid or expired {order_id}")
        return "Order has been paid or expired"

    try:
        session, payment = stripe_session_check(order=order, user=user)
    except Exception as e:
        logger.exception(f'Error: {e}')
        return "Something went wrong"
    return f"[Payment order {order_id}]({session.url})"
