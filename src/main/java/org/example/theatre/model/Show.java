package org.example.theatre.model;

import org.springframework.data.cassandra.core.mapping.PrimaryKey;
import org.springframework.data.cassandra.core.mapping.PrimaryKeyColumn;
import org.springframework.data.cassandra.core.mapping.Table;

import java.util.UUID;

@Table("shows")
public class Show {
    @PrimaryKeyColumn(name = "show_date", ordinal = 0)
    private String showDate;

    @PrimaryKeyColumn(name = "show_time", ordinal = 1)
    private String showTime;

    @PrimaryKeyColumn(name = "show_id", ordinal = 2)
    private UUID showId;

    private String title;

    // Getters and setters
}
