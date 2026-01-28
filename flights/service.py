from typing import List, Dict, Any
from .models import Flights


base_url = 'https://else-semisolemn-meta.ngrok-free.dev/api/docs/#/Orders/v1_orders_create'


def get_active_flight() -> List[Dict[str, Any]]:
    """
        Retrieves a list of all currently scheduled (active) flights.
        Use this tool when the user asks about available flights generally, without specific filters.

        Returns:
            List[Dict]: A list of flight dictionaries containing details.
    """
    active_flight = Flights.objects.filter(flight_status=Flights.StatusChoice.SCHEDULED)
    if not active_flight.exists():
        return []
    response = []
    for flight in active_flight:
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
