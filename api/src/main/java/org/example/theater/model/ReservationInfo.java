package com.example.theater.model;

import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.Table;

import java.util.UUID;

@Table("reservations_info")
public class ReservationInfo {
    @PrimaryKey
    private UUID reservationId;
    private UUID showId;
    private int ticketsCount;
    private String userName;
    private String email;
    private long reservationTime;

    // Getters and setters
}
