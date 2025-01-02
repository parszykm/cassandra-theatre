CREATE KEYSPACE IF NOT EXISTS theatre
    WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 3 };

USE theatre;

CREATE TABLE IF NOT EXISTS shows (
    show_id UUID,
    show_date DATE,
    show_time TIME,
    title TEXT,
    PRIMARY KEY ((show_date, show_time), show_id)
) WITH CLUSTERING ORDER BY (show_id ASC);

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
    PRIMARY KEY ((seat_reservation_time), reservation_id, seat_id)
) WITH CLUSTERING ORDER BY (reservation_id ASC);

CREATE TABLE IF NOT EXISTS reservations_info (
    reservation_id UUID,
    show_id UUID,
    tickets_count INT,
    user_name TEXT,
    email TEXT,
    reservation_time TIMESTAMP,
    PRIMARY KEY ((reservation_id), show_id, reservation_time)
) WITH CLUSTERING ORDER BY (show_id DESC, reservation_time DESC);
