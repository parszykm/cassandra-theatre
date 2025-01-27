from locust import HttpUser, task, between
import random
import json
import uuid

class ReservationUser(HttpUser):
    # Wait time between tasks (simulates user pacing)
    wait_time = between(1, 5)

    # Placeholder for cached available seats and show ID
    available_seats = []
    show_id = None

    def on_start(self):
        """
        Initialize the user by getting available seats for a show.
        """
        # Define the show ID for which reservations will be made
        self.show_id = "YOUR_SHOW_ID_HERE"  # Replace with the actual show_id
        self.update_available_seats()

    def update_available_seats(self):
        """
        Fetch available seats from the server and update the local cache.
        """
        response = self.client.get(f"/seats?show_id={self.show_id}")
        if response.status_code == 200:
            self.available_seats = response.json()
        else:
            print("Failed to fetch available seats!")

    @task(1)
    def make_reservation(self):
        """
        Simulate a user attempting to make a reservation.
        """
        if not self.available_seats:
            self.update_available_seats()

        # If no seats are available, exit the task early
        if not self.available_seats:
            print("No seats available for reservation!")
            return

        # Pick a random number of seats to reserve (e.g., 1-3 seats)
        num_seats = random.randint(1, min(3, len(self.available_seats)))

        # Select random seats from the available pool
        seats_to_reserve = random.sample(self.available_seats, num_seats)

        # Create the reservation payload
        reservation_payload = {
            "email": f"user{random.randint(1, 1000)}@example.com",  # Unique user emails
            "user_name": f"User {random.randint(1, 1000)}",
            "show_id": self.show_id,
            "seats": seats_to_reserve
        }

        # Send a POST request to the reservations endpoint
        response = self.client.post("/reservations", json=reservation_payload)
        if response.status_code == 201:
            print(f"Reservation successful for seats: {seats_to_reserve}")
            # Remove reserved seats from available_seats cache
            self.available_seats = [seat for seat in self.available_seats if seat not in seats_to_reserve]
        elif response.status_code == 409:
            print(f"Conflict: Some seats already reserved: {seats_to_reserve}")
            # Refresh the available seats
            self.update_available_seats()
        else:
            print(f"Reservation failed: {response.status_code} - {response.text}")
