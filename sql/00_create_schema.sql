CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.bookings_raw (
    booking_id TEXT,
    booking_datetime TIMESTAMP,
    booking_status TEXT,
    customer_id TEXT,
    vehicle_type TEXT,
    pickup_location TEXT,
    drop_location TEXT,
    booking_value NUMERIC(12, 2),
    payment_method TEXT,
    ride_distance_km NUMERIC(10, 2),
    driver_rating NUMERIC(3, 2),
    customer_rating NUMERIC(3, 2),
    source_file TEXT NOT NULL,
    load_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.bookings (
    booking_id VARCHAR(13) PRIMARY KEY,
    booking_datetime TIMESTAMP NOT NULL,
    booking_status_normalized VARCHAR(32) NOT NULL CHECK (
        booking_status_normalized IN (
            'Success',
            'Canceled by Customer',
            'Canceled by Driver',
            'Driver Not Found'
        )
    ),
    customer_id TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    pickup_location TEXT,
    drop_location TEXT,
    booking_value NUMERIC(12, 2),
    payment_method TEXT,
    ride_distance_km NUMERIC(10, 2),
    driver_rating NUMERIC(3, 2) CHECK (driver_rating BETWEEN 0 AND 5),
    customer_rating NUMERIC(3, 2) CHECK (customer_rating BETWEEN 0 AND 5),
    is_incomplete_ride BOOLEAN NOT NULL DEFAULT FALSE,
    completed_revenue NUMERIC(12, 2) NOT NULL DEFAULT 0,
    quality_issue_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW analytics.kpi_revenue AS
SELECT
    COUNT(*) AS total_bookings,
    COUNT(*) FILTER (WHERE booking_status_normalized = 'Success' AND NOT is_incomplete_ride) AS completed_rides,
    COALESCE(SUM(completed_revenue), 0) AS completed_revenue
FROM core.bookings;

-- Revenue is a SUM of eligible completed booking values, never COUNT(booking_value).
