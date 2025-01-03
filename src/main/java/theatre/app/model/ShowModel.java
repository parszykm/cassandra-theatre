package theatre.app.model;

import java.util.UUID;

public class ShowModel {
    private UUID showId;
    private String title;
    private String showDate;
    private String showTime;

    public ShowModel(UUID showId, String title, String showDate, String showTime) {
        this.showId = showId;
        this.title = title;
        this.showDate = showDate;
        this.showTime = showTime;
    }

    // Getters and Setters
    public UUID getShowId() {
        return showId;
    }

    public void setShowId(UUID showId) {
        this.showId = showId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getShowDate() {
        return showDate;
    }

    public void setShowDate(String showDate) {
        this.showDate = showDate;
    }

    public String getShowTime() {
        return showTime;
    }

    public void setShowTime(String showTime) {
        this.showTime = showTime;
    }
}
