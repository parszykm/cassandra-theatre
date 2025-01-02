package org.example.theatre.controller;

import org.example.theatre.repository.ReservationInfoRepository;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/reservation")
public class ReservationController {
    private final ReservationInfoRepository reservationInfoRepository;

    public ReservationController(ReservationInfoRepository reservationInfoRepository) {
        this.reservationInfoRepository = reservationInfoRepository;
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
