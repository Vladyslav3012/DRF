import logging
from typing import List, Dict, Any

from channels.db import database_sync_to_async

from Project.settings import ACTIVE_DOMAIN
from .models import Flights

logger = logging.getLogger(__name__)
base_url = f'{ACTIVE_DOMAIN}/api/docs/#/Orders/v1_orders_create'


@database_sync_to_async
def _get_flights_from_db():
    active_flights = Flights.objects.filter(flight_status=Flights.StatusChoice.SCHEDULED)

    results = []
    for flight in active_flights:
        results.append({
            "id": flight.id,
            "City_departure": flight.city_departure,
            "Time departure": flight.time_departure.strftime("%d-%m-%Y %H:%M:%S"),
            "City arrival": flight.city_arrival,
            "Time arrival": flight.time_arrival.strftime("%d-%m-%Y %H:%M:%S"),
            "Average price": float(flight.average_price),
            "Count free ticket": flight.total_tickets,
            "booking_link": base_url
        })
    return results


async def get_active_flight() -> List[Dict[str, Any]]:
    """
        Retrieves a list of all currently scheduled (active) flights.
        Use this tool when the user asks about available flights generally, without specific filters.

        Returns:
            List[Dict]: A list of flight dictionaries containing details.
    """
    """
        Retrieves a list of all currently scheduled (active) flights.
        Use this tool when the user asks about available flights generally.
        """
    try:
        flights_data = await _get_flights_from_db()

        return flights_data

    except Exception as e:
        logger.exception(f"Gemini tools error {e}")
        return []


def search_flight(city_departure: str | None = None,
                  city_arrival: str | None = None,
                  time_departure: str | None = None) -> List[Dict[str, Any]]:
    """
        Searches for flights based on departure city, arrival city, or a specific date.

        Args:
            city_departure: The name of the city the flight departs from (e.g., 'Kyiv').
            city_arrival: The name of the city the flight arrives at (e.g., 'Warsaw').
            time_departure: The specific date of departure in 'YYYY-MM-DD' format (e.g., '2026-05-20').

        Returns:
            List[Dict]: A list of flights matching the criteria.
    """
    all_flights = Flights.objects.all()

    if city_departure is not None:
        all_flights = all_flights.filter(city_departure=city_departure)

    if city_arrival is not None:
        all_flights = all_flights.filter(city_arrival=city_arrival)

    if time_departure is not None:
        all_flights = all_flights.filter(time_departure__gte=time_departure)

    response = []
    for flight in all_flights:
        response.append({"id": flight.id,
                         "City_departure": flight.city_departure,
                         "Time departure": flight.time_departure.strftime("%d-%m-%Y %H:%M:%S"),
                         "City arrival": flight.city_arrival,
                         "Time arrival": flight.time_arrival.strftime("%d-%m-%Y %H:%M:%S"),
                         "Average price": float(flight.average_price),
                         "Count free ticket": flight.total_tickets,
                         "booking_link": base_url
                         })

    return response
