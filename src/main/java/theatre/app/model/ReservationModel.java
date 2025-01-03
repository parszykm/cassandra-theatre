package theatre.app.model;

import java.util.UUID;

public class ReservationModel {
    private UUID reservationId;
    private UUID showId;
    private long reservationTime;
    private int ticketsCount;
    private String userName;
    private String email;
}