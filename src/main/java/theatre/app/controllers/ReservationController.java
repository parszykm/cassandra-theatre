package theatre.app.controllers;

import org.springframework.web.bind.annotation.*;
import theatre.app.model.*;

@RestController
@RequestMapping("/reservation")
public class ReservationController {
    private final ReservationModel reservationModel;

    public ReservationController(ReservationModel reservationModel) {
        this.reservationModel = reservationModel;
    }

    @GetMapping
    public String getAllReservations() {
        return "Placeholder for retrieving all reservations";
    }

    @PostMapping
    public String createReservation() {
        return "Placeholder for creating a new reservation";
    }
}