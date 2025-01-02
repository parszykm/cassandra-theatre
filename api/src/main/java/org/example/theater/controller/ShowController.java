package com.example.theater.controller;

import com.example.theater.repository.ShowRepository;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/shows")
public class ShowController {
    private final ShowRepository showRepository;

    public ShowController(ShowRepository showRepository) {
        this.showRepository = showRepository;
    }

    @GetMapping
    public String getAllShows() {
        return "Placeholder for retrieving all shows";
    }

    @PostMapping
    public String createShow() {
        return "Placeholder for creating a new show";
    }
}
