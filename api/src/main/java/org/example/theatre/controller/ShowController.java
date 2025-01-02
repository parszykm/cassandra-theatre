package org.example.theatre.controller;

import org.example.theatre.model.Show;
import org.example.theatre.repository.ShowRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/shows")
public class ShowController {
    private final ShowRepository showRepository;

    public ShowController(ShowRepository showRepository) {
        this.showRepository = showRepository;
    }

    @GetMapping
    public List<Show> getAllShows() {

        return showRepository.findAll();
    }

    @PostMapping
    public String createShow() {
        return "Placeholder for creating a new show";
    }
}
