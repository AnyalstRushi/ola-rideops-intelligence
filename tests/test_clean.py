import pandas as pd
import pytest

from ola_rideops.clean import clean_bookings


def test_invalid_booking_ids_are_quarantined():
    df = pd.DataFrame({"BookingID": ["BAD-1"], "BookingStatus": ["Success"]})
    result = clean_bookings(df)
    assert result.loc[0, "record_disposition"] == "quarantine_invalid_booking_id"


def test_status_is_normalized():
    df = pd.DataFrame(
        {"BookingID": ["CNR1234567890"], "BookingStatus": [" cancelled by customer "]}
    )
    result = clean_bookings(df)
    assert result.loc[0, "booking_status_normalized"] == "Canceled by Customer"


def test_exact_duplicates_are_flagged():
    df = pd.DataFrame(
        {
            "BookingID": ["CNR1234567890", "CNR1234567890"],
            "BookingStatus": ["Success", "Success"],
        }
    )
    result = clean_bookings(df)
    assert result["exact_duplicate_flag"].sum() == 1


def test_missing_required_columns_raise_error():
    with pytest.raises(ValueError, match="booking_status"):
        clean_bookings(pd.DataFrame({"BookingID": ["CNR1234567890"]}))
