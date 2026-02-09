from typing import List, Dict, Any
from orders.models import Order
from users.models import CustomUser


def get_user_order(user_id: int) -> List[Dict[str, Any]]:
    """
        Retrieves the complete history of flight orders/bookings for a specific user.
        Use this tool when the user asks: "Show my tickets", "Do I have any bookings?", or "What are my orders?".

        Args:
            user_id: The unique ID of the currently authenticated user.

        Returns:
            List[Dict]: A list of orders with detailed ticket information.
    """
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        return []
    orders = (Order.objects.filter(owner=user)
              .prefetch_related('tickets')
              .order_by("-created_at"))
    if not orders.exists():
        return []

    res = []

    for order in orders:
        ticket_data = []
        for ticket in order.tickets.all():
            ticket_data.append(
                {
                    "Ticket": ticket.id,
                    "Fight": ticket.flight.id,
                    "Seat": ticket.seat_number,
                    "Class": ticket.ticket_class,
                })
        res.append({
            "Order": str(order.order_id),
            "Total price": float(order.total_price),
            "Status": order.status,
            "Currency": order.currency,
            "Tickets": ticket_data
        })

    return res
