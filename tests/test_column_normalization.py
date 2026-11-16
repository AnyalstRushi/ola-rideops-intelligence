import pytest

from ola_rideops.clean import _to_snake_case


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("BookingID", "booking_id"),
        ("BookingStatus", "booking_status"),
        ("Booking ID", "booking_id"),
        ("booking_id", "booking_id"),
        ("BOOKING_ID", "booking_id"),
        ("CustomerID", "customer_id"),
        ("HTTPResponseCode", "http_response_code"),
        (" Booking  ID ", "booking_id"),
    ],
)
def test_column_normalization_preserves_acronyms(source, expected):
    assert _to_snake_case(source) == expected
