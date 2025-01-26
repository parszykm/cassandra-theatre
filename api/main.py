from flask import Flask, jsonify, request
from collections import defaultdict
from cassandra.cluster import Cluster
import configparser
import sys
import uuid
from datetime import datetime
import string
import threading
import time
from enum import Enum
from datetime import datetime, timedelta


class Status(Enum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    SOLD = 'sold'

class BackendSession:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('cluster.config')
        self.contact_point = config['ClusterConfig']['contact_point']
        self.keyspace = config['ClusterConfig']['keyspace']
        try:
            self.cluster = Cluster([self.contact_point])
            self.session = self.cluster.connect(self.keyspace)
        except Exception as e:
            print(f"Couldn't connect to cluster:{e}", file=sys.stderr)

    def resolve_conflicts(self,show_id):
        try:
            winning_reservations, losing_reservations = self.get_winning_reservations(show_id)
            for winning_reservation in winning_reservations:
                get_seats_query = """
                SELECT seat_id
                FROM reservations_by_user
                where reservation_id = %s
                ALLOW FILTERING
                """

                update_seat_query = """
                UPDATE seats_by_show
                SET reservation_id = %s, status = 'sold'
                WHERE show_id = %s AND seat_id = %s
                """
                rows = self.session.execute(get_seats_query, (uuid.UUID(winning_reservation),))

                resolved_reservations_cache.append(winning_reservation)

                for row in rows:
                    seat_id = row.seat_id
                    self.session.execute(update_seat_query, (uuid.UUID(winning_reservation), show_id, seat_id))

            for losing_reservation in losing_reservations:
                resolved_reservations_cache.append(losing_reservation)
                print("Sending information about unsuccessful reservation to reservation:", losing_reservation)
        except Exception as e:
            print(f"Error while resolving conflicts for show {show_id}: {e}", file=sys.stderr)
            return None


    def get_winning_reservations(self, show_id):
        try:
            grouped_reservations, winning_reservations = self.get_seat_groups_with_multiple_reservations(show_id)
            if grouped_reservations is None:
                return None

            losing_reservations = []

            for seat_id, reservations in grouped_reservations.items():
#check if seat_id is not already taken
                get_seat_query =  """
                SELECT seat_id, status, reservation_id
                FROM seats_by_show
                where seat_id = %s and show_id = %s
                """
                seat_already_taken = False
                seats = self.session.execute(get_seat_query,(seat_id, show_id))

                for seat in seats:
                    if seat.status == 'sold':
                        seat_already_taken = True
                        previous_winner = seat.reservation_id

                reservation_ids = [row['reservation_id'] for row in reservations]

                if seat_already_taken:
                    for reservation_id in reservation_ids:
                        losing_reservations.append(reservation_id)
                    if previous_winner in losing_reservations:
                        losing_reservations.remove(previous_winner)
                        continue

                reservations_query = """
                SELECT reservation_id, reservation_time
                FROM reservations_info
                WHERE reservation_id = %s
                ALLOW FILTERING
                """
                reservation_details = []
                for reservation_id in reservation_ids:
                    rows = self.session.execute(reservations_query, (uuid.UUID(reservation_id),))
                    for row in rows:
                        print(row)
                        reservation_details.append({
                            "reservation_id": str(row.reservation_id),
                            "reservation_time": row.reservation_time
                        })

                earliest_reservation = min(reservation_details, key=lambda x: x['reservation_time'])

                for reservation_id in reservation_ids:
                    if reservation_id in winning_reservations:
                        winning_reservations.remove(reservation_id)
                    losing_reservations.append(reservation_id)

                winning_reservations.append(earliest_reservation["reservation_id"])

                if earliest_reservation["reservation_id"] in losing_reservations:
                    losing_reservations.remove(earliest_reservation["reservation_id"])
            
            return winning_reservations, losing_reservations

        except Exception as e:
            print(f"Error while analyzing seat reservations for show {show_id}: {e}", file=sys.stderr)
            return None
    def get_seat_groups_with_multiple_reservations(self, show_id):
        try:
            reservations = self.get_reservations_for_show(show_id)
            if reservations is None:
                return None

            grouped_reservations = defaultdict(list)
            for reservation in reservations:
                grouped_reservations[reservation['seat_id']].append(reservation)

            filtered_groups = {seat_id: res_list for seat_id, res_list in grouped_reservations.items() if len(res_list) > 1}

            reservation_ids_in_filtered_groups = {
                reservation['reservation_id']
                for res_list in filtered_groups.values()
                for reservation in res_list
            }

            remaining_reservation_ids = [
                reservation['reservation_id']
                for reservation in reservations
                if reservation['reservation_id'] not in reservation_ids_in_filtered_groups
            ]
            
            return filtered_groups, remaining_reservation_ids
        except Exception as e:
            print(f"Error while grouping reservations for show {show_id}: {e}", file=sys.stderr)
            return None
    def get_reservations_for_show(self, show_id):
        print("get_reservations_for_show:")
        try:
            # query = """
            # SELECT reservation_id, seat_id, seat_reservation_time
            # FROM reservations_by_user
            # WHERE show_id = %s
            # ALLOW FILTERING
            # """
            # #trzeba dodac show_id do klucza
            # rows = self.session.execute(query, (uuid.UUID(show_id),))

            query = """
            SELECT reservation_id, seat_id, seat_reservation_time
            FROM reservations_by_user
            WHERE show_id = %s
            AND seat_reservation_time <= %s
            AND seat_reservation_time > %s
            ALLOW FILTERING
            """

            now = datetime.utcnow()
            five_minutes_ago = now - timedelta(minutes=4)
            ten_minutes_ago = now - timedelta(minutes=10)

            rows = self.session.execute(query, (uuid.UUID(show_id), five_minutes_ago, ten_minutes_ago))
            #### jesli chcemy po czasie

            results = []
            for row in rows:
                obj = {
                "reservation_id": str(row.reservation_id),
                "seat_id": row.seat_id,
                "seat_reservation_time": str(row.seat_reservation_time)
                }

                if obj["reservation_id"] not in resolved_reservations_cache:
                    results.append(obj)

            print(results)
            return results

        except Exception as e:
            print(f"Error while fetching reservations for show {show_id}: {e}", file=sys.stderr)
            return None
    def get_all_shows(self):
        try:
            query = "SELECT * FROM shows"
            rows = self.session.execute(query)
            return [{"show_id": str(row.show_id),
                     "show_date": str(row.show_date),
                     "show_time": str(row.show_time),
                     "title": row.title} for row in rows]
        except Exception as e:
            print(f"Error fetching shows: {e}", file=sys.stderr)
            return []
    def add_show(self, show_date, show_time, title):
        try:
            show_date = datetime.strptime(show_date, "%d/%m/%Y").date()
            show_time = datetime.strptime(show_time, "%H:%M:%S").time()
        
            query = """
            INSERT INTO shows (show_id, show_date, show_time, title)
            VALUES (%s, %s, %s, %s)
            """
            show_id = uuid.uuid4()
            self.session.execute(query, (show_id, show_date, show_time, title))
            self.populate_seats_for_show(show_id)
            
            return str(show_id)
        except Exception as e:
            print(f"Error adding show: {e}", file=sys.stderr)
            return None
    def populate_seats_for_show(self, show_id, rows=5, total_seats=10):
            try:
                query = """
                INSERT INTO seats_by_show (show_id, seat_id, seat_number, status)
                VALUES (%s, %s, %s, %s)
                """
                for row in range(rows):
                    for seat_number in range(1, total_seats + 1):
                        seat_id = f"{string.ascii_uppercase[row]}-{seat_number}"
                        status = "available"
                        self.session.execute(query, (show_id, seat_id, seat_number, status))
            except Exception as e:
                print(f"Error populating seats for show {show_id}: {e}", file=sys.stderr)
                return None
    def get_seats(self, show_id, status=Status.AVAILABLE.value):
        try:
            query="""
            SELECT seat_id, status FROM seats_by_show
            WHERE show_id = %s
            """
            rows = self.session.execute(query, (show_id,))
            seats_available = [row for row in rows if str(row.status) == status]
            return [str(row.seat_id) for row in seats_available]
        except Exception as e:
            print(f"Could not get the seats: {e}", file=sys.stderr)
            return None
        
    def get_reservations(self, email):
        try:
            query = """
            SELECT show_id, tickets_count, reservation_id, reservation_time FROM reservations_info
            WHERE email=%s
            """
            result = []
            rows = self.session.execute(query, (email))
            for row in rows:
                reservation_id = uuid.UUID(row.reservation_id)
                show_id = uuid.UUID(row.show_id)
                reservation = {
                    "email": email,
                    "tickets": str(row.tickets_count),
                    "reservation_time": str(row.reservation_time)
                    }
                
                query = """
                SELECT title FROM shows
                WHERE show_id=%s
                """
                show = self.session.execute(query, (show_id))
                reservation["title"] = str(show[0].title)
                
                query = """
                SELECT seat_id FROM reservations_by_user
                WHERE reservation_id=%s
                """
                
                seats_rows = self.session.execute(query, (reservation_id))
                seats = []
                for seat in seats_rows:
                    seats.append(str(seat.seat_id))
                reservation["seats"] = seats
                result.append(reservation)
            return result
        except Exception as e:
            print(f"Error while getting reservation: {e}")
            return None
    def check_seats_availability(self, show_id, seats):
        available_seats = set(self.get_seats(show_id))
        print(available_seats)
        print(seats)
        print(all(seat in available_seats for seat in seats))
        return all(seat in available_seats for seat in seats)
    def make_reservation(self, email, show_id, seats, user_name):
        try:
            query_insert_reservation = """
            INSERT INTO reservations_by_user (reservation_id, show_id, seat_reservation_time, seat_id)
            VALUES (%s, %s, %s, %s)
            """
            query_update_seat = """
            UPDATE seats_by_show SET status = %s WHERE show_id = %s AND seat_id = %s
            """
            query_insert_info = """
            INSERT INTO reservations_info (reservation_id, show_id, tickets_count, user_name, email, reservation_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            reservation_id = uuid.uuid4()
            reservation_time = datetime.now()
            show_id = uuid.UUID(show_id) 

            # Check if the chosen seats are available
            # if not self.check_seats_availability(show_id, seats):
            #     return 1
            #COMMENTED FOR TEST PURPOUSE

            for seat in seats:
                self.session.execute(query_insert_reservation, (reservation_id, show_id, reservation_time, seat))
                self.session.execute(query_update_seat, (Status.RESERVED.value, show_id, seat))
                
            ticket_count = len(seats)
            self.session.execute(query_insert_info, (reservation_id, show_id, ticket_count, user_name, email, reservation_time))

            return 0
        except Exception as e:
            print(f"Error while creating reservation: {e}")
            return 2  
app = Flask(__name__)

resolved_reservations_cache = []
shows_to_observe_cache = []
is_task_running = False

@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):
		return jsonify({'description': 'Cassandra Theatre API'})


@app.route('/shows', methods = ['GET', 'POST'])
def shows():
    backend = BackendSession()
    if request.method == 'GET':
        shows = backend.get_all_shows()
        return jsonify({'shows': shows})
    elif request.method == 'POST':
            data = request.json
            show_date = data.get('show_date')
            show_time = data.get('show_time')
            title = data.get('title')
            print(data)
            if not show_date or not show_time or not title:
                return jsonify({'error': 'Missing required fields: show_date, show_time, title'}), 400
            
            try:
                show_id = backend.add_show(show_date, show_time, title)
                if show_id is not None:
                    shows_to_observe_cache.append(show_id)
                    return jsonify({'message': 'Show added successfully', 'show_id': show_id}), 201
                else:
                    return jsonify({'error': f'Could not add the show'}), 500
            except Exception as e:
                return jsonify({'error': f'Could not add the show: {e}'}), 500
        
@app.route('/reservations', methods=['GET','POST'])
def reservations():
    backend = BackendSession()
    data = request.json
    if request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Missing required parameter: email'}), 400
        reservations = backend.get_reservations(email=email)
        if reservations is not None:
            return jsonify(reservations), 200
        else:
            return jsonify({'error': 'Could not get reservations'}), 500
    elif request.method == 'POST':
        email = data['email']
        user_name = data['user_name']
        show_id = data['show_id']
        seats = data['seats']
        rc = backend.make_reservation(email, show_id, seats, user_name)
        if rc == 0:
            return jsonify({'message': 'The reservation has been created'}), 201
        elif rc == 1:
            return jsonify({'error': 'At least one of the chosen seats has been already reserved'}), 409
        elif rc == 2:
            return jsonify({'error': 'Error while making reservation'}), 500
        
@app.route('/seats', methods=['GET'])
def seats():
    backend = BackendSession()
    show_id = uuid.UUID(request.args.get('show_id'))
    if not show_id:
        return jsonify({'error': 'Missing required parameter: show_id'}), 400
    seats = backend.get_seats(show_id)
    if seats is not None:
        return jsonify(seats), 200
    else:
        return jsonify({'error': 'Could not get the seats'}), 500

@app.route('/resolve_conflicts', methods=['GET'])
def resolve():
    backend = BackendSession()
    show_id = uuid.UUID(request.args.get('show_id'))
    if not show_id:
        return jsonify({'error': 'Missing required parameter: show_id'}), 400
    backend.resolve_conflicts(show_id)
    return jsonify("Resolving conflicts"), 200

def resolve_conflicts_task(app_context, show_id):
    with app_context:
        print("Resolving task initialized for show: ",show_id)
        backend = BackendSession()
        backend.resolve_conflicts(show_id)
        print("Finished resolving conflicts for show: ", show_id)


def generate_conflict_resolving_tasks(app_context): 
    global is_task_running
    if not is_task_running:
        is_task_running = True

        print("Conflicts resolving task initalized.")
    
        with app_context:
            while True:
                for show in shows_to_observe_cache:
                    print("Resolving conflicts for a show: ", show)
                    task = threading.Thread(target=resolve_conflicts_task, args=(app_context,show), daemon = True)
                    task.start()

                print("Sleeping 5 minutes before next conflicts resolving.")
                time.sleep(1*60)

        
if __name__ == '__main__':
    app_context = app.app_context()
    app_context.push()

    generator_task = threading.Thread(target=generate_conflict_resolving_tasks, args=(app_context,), daemon=True)
    generator_task.start()

    app.run(debug = True,host='0.0.0.0', port=8080)
    