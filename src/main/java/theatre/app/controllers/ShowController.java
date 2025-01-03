package theatre.app.controllers;

import theatre.app.model.ShowModel;
import theatre.app.repositories.ShowRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/shows")
public class ShowController {
    private final ShowRepository showRepository;

    public ShowController(ShowRepository showRepository) {
        this.showRepository = showRepository;
    }

    @GetMapping
    public List<ShowModel> getAllShows() {
        return showRepository.getAllShows();
    }
}
