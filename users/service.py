from google import genai
import logging
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from Project import settings
from Project.settings import PROMPT_TO_TITLE
from users.models import Order, Payment
import stripe

logger = logging.getLogger(__name__)

YOUR_DOMAIN = 'https://else-semisolemn-meta.ngrok-free.dev'
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_session_check(order, user):
    line_items = []
    tickets = order.tickets.all()

    payment = order.payments.order_by("-created_at").first()

    if (
        payment
        and payment.stripe_checkout_session
        and payment.session_expires_at
        and payment.session_expires_at > timezone.now()
):
        session = stripe.checkout.Session.retrieve(payment.stripe_checkout_session)
        logger.info(f"Select exists active payment #{payment.payment_id} to this order")
        return session, payment

    elif not payment:
        payment = Payment.objects.create(order=order,
                                     owner=user,
                                     price=sum([ticket.price for ticket in tickets]),
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
            "order_id": str(order.order_id),
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
    meta = session.get("metadata", {})

    order_id = meta.get("order_id")
    payment_id = meta.get("payment_id")
    session_id = session["id"]
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

        logger.info(f"Payment {payment.payment_id} success, order_updated={updated}")

        return JsonResponse({'msg': 'Order payment success'}, status=200)

    if event_type == "checkout.session.expired":
        updated = Order.objects.filter(
            order_id=order_id,
            stripe_checkout_session=session_id
        ).update(status="Expired")

        payment.status_payment = "Canceled"
        payment.save(update_fields=["status_payment"])

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
        logger.exception("Error")
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"msg": "Checkout session expired"}, status=200)


client = genai.Client(api_key=settings.GEMINI_SECRET_KEY)
SYSTEM_PROMPT = settings.SYSTEM_PROMPT
PROMPT_TO_TITLE = PROMPT_TO_TITLE


def create_title(model, user_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=PROMPT_TO_TITLE,
                candidate_count=1
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return user_prompt[:50]
    except Exception:
        return user_prompt[:50]


def ask_to_gemini(model, user_prompt):
    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config = genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        if response.text:
            return response.text.strip().replace('"', '')
        return "Answer not generated"
    except Exception:
        return "An error occurred while accessing the service"