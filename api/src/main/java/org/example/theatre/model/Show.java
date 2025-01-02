package org.example.theatre.model;

import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.PrimaryKeyColumn;
import org.springframework.data.cassandra.core.mapping.Table;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

@Table("shows")
public class Show {
    @PrimaryKeyColumn(name = "show_date", ordinal = 0)
    private LocalDate showDate;

    @PrimaryKeyColumn(name = "show_time", ordinal = 1)
    private LocalTime showTime;

    @PrimaryKey
    private UUID showId;

    private String title;

    // Getters and setters
}