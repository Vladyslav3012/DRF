import os
import pytest
from django.urls import reverse
from orders.models import Payment
from orders.tests.factories import OrderFactory


TEST_TOKEN = os.environ['SECRET_TOKEN_TO_WEBHOOK']


@pytest.mark.django_db
def test_webhook_check_valid_session(api_client, mocker):
    test_session_id = 'test_session_id_123'

    order = OrderFactory(stripe_checkout_session=test_session_id)

    payment = Payment.objects.create(
        owner=order.owner,
        order=order,
        stripe_checkout_session=test_session_id,
        price=order.total_price,
        status_payment="Pending"
    )

    url = reverse('stripe-webhook', kwargs={'token': TEST_TOKEN})

    full_event_dict = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": test_session_id,
                "customer_details": {
                    "email": "test@example.com"
                },
                "metadata": {
                    "order_id": str(order.order_id),
                    "payment_id": str(payment.payment_id)
                }
            }
        }
    }

    mocker.patch('stripe.Webhook.construct_event', return_value=full_event_dict)

    api_client.defaults['HTTP_STRIPE_SIGNATURE'] = 'fake_signature'

    response = api_client.post(url, data={}, format='json')

    assert response.status_code == 200

    order.refresh_from_db()
    payment.refresh_from_db()

    assert order.status == "Confirmed"
    assert payment.status_payment == "Confirmed"
    assert payment.payed_at is not None
