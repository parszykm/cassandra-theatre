package org.example.theatre.model;

import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.Table;

import java.util.UUID;

public class ReservationInfo {

    @PrimaryKeyColumn(name = "reservation_id", ordinal = 0)
    private UUID reservationId;

    @PrimaryKeyColumn(name = "show_id", ordinal = 1)
    private UUID showId;

    @PrimaryKeyColumn(name = "reservation_time", ordinal = 2)
    private long reservationTime;

    private int ticketsCount;
    private String userName;
    private String email;
}