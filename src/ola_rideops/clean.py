import re

import pandas as pd

NULL_TOKENS = {"", "null", "n/a", "na", "none", "-"}
BOOKING_ID_PATTERN = re.compile(r"^CNR\d{10}$")

STATUS_MAP = {
    "success": "Success",
    "canceled by customer": "Canceled by Customer",
    "cancelled by customer": "Canceled by Customer",
    "canceled by driver": "Canceled by Driver",
    "cancelled by driver": "Canceled by Driver",
    "driver not found": "Driver Not Found",
}


def normalize_text(value):
    """Trim text, collapse whitespace, and map null-like tokens to pandas NA."""
    if pd.isna(value):
        return pd.NA
    value = re.sub(r"\s+", " ", str(value).strip())
    return pd.NA if value.lower() in NULL_TOKENS else value


def normalize_status(value):
    """Map source status spellings to a governed status vocabulary."""
    value = normalize_text(value)
    return STATUS_MAP.get(str(value).lower(), pd.NA) if not pd.isna(value) else pd.NA


def _to_snake_case(name):
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", str(name))
    return re.sub(r"_+", "_", name.replace(" ", "_")).strip("_").lower()


def clean_bookings(df):
    """Apply initial, auditable standardisation and critical-record routing."""
    out = df.copy()
    out.columns = [_to_snake_case(column) for column in out.columns]
    out = out.map(normalize_text)

    required = {"booking_id", "booking_status"}
    missing = required.difference(out.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out["booking_status_normalized"] = out["booking_status"].map(normalize_status)
    out["booking_id_valid"] = out["booking_id"].astype("string").str.match(
        BOOKING_ID_PATTERN, na=False
    )
    out["exact_duplicate_flag"] = out.duplicated(keep="first")
    out["record_disposition"] = "clean"
    out.loc[out["exact_duplicate_flag"], "record_disposition"] = "exact_duplicate_removed"
    out.loc[~out["booking_id_valid"], "record_disposition"] = "quarantine_invalid_booking_id"
    out.loc[out["booking_status_normalized"].isna(), "record_disposition"] = "quarantine_invalid_status"
    return out
