CREATE TABLE IF NOT EXISTS shows (
    show_id UUID,
    show_date DATE,
    show_time TIME,
    title TEXT,
    PRIMARY KEY ((show_date, show_time), show_id)
);

CREATE TABLE IF NOT EXISTS seats_by_show (
    show_id UUID,
    seat_id TEXT,
    seat_number INT,
    status TEXT, -- possible values: 'available', 'reserved', 'sold'
    reservation_id UUID,
    reservation_time TIMESTAMP,
    PRIMARY KEY ((show_id), seat_id)
) WITH CLUSTERING ORDER BY (seat_id ASC);

CREATE TABLE IF NOT EXISTS reservations_by_user (
    reservation_id UUID,
    show_id UUID,
    seat_id TEXT,
    seat_reservation_time TIMESTAMP,
    PRIMARY KEY ((reservation_id), show_id, seat_id)
) WITH CLUSTERING ORDER BY (seat_id ASC);

CREATE TABLE IF NOT EXISTS reservations_info (
    reservation_id UUID,
    show_id UUID,
    tickets_count INT,
    user_name TEXT,
    email TEXT,
    reservation_time TIMESTAMP,
    PRIMARY KEY ((reservation_id), show_id)
) WITH CLUSTERING ORDER BY (reservation_time DESC);
