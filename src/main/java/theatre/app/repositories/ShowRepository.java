package theatre.app.repositories;

import com.datastax.driver.core.BoundStatement;
import com.datastax.driver.core.PreparedStatement;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import org.springframework.stereotype.Repository;
import theatre.app.backend.BackendSession;
import theatre.app.model.ShowModel;

import java.util.ArrayList;
import java.util.List;

@Repository
public class ShowRepository {

    private final BackendSession backendSession;
    private PreparedStatement SELECT_ALL_SHOWS;

    public ShowRepository(BackendSession backendSession) {
        this.backendSession = backendSession;

        try {
            SELECT_ALL_SHOWS = backendSession.session.prepare("SELECT * FROM shows;");
        } catch (Exception e) {
            throw new RuntimeException("Could not prepare query statements: " + e.getMessage(), e);
        }
    }

    public List<ShowModel> getAllShows() {
        List<ShowModel> shows = new ArrayList<>();
        BoundStatement bs = new BoundStatement(SELECT_ALL_SHOWS);
        ResultSet rs = backendSession.session.execute(bs);

        for (Row row : rs) {
            ShowModel show = new ShowModel(
                    row.getUUID("showId"),
                    row.getString("title"),
                    row.getString("showDate"),
                    row.getString("showTime")
            );
            shows.add(show);
        }
        return shows;
    }
}
