from flask import Flask, jsonify, request
from cassandra.cluster import Cluster
import configparser
import sys
import uuid

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
            query = """
            INSERT INTO shows (show_id, show_date, show_time, title)
            VALUES (%s, %s, %s, %s)
            """
            show_id = uuid.uuid4()  # Generate a unique ID for the show
            self.session.execute(query, (show_id, show_date, show_time, title))
            self.populate_seats_for_show()
            
            return str(show_id)
        except Exception as e:
            print(f"Error adding show: {e}", file=sys.stderr)
            return None
    def populate_seats_for_show(self, show_id, total_seats=20):
            try:
                query = """
                INSERT INTO seats_by_show (show_id, seat_id, seat_number, status)
                VALUES (%s, %s, %s, %s)
                """
                for seat_number in range(1, total_seats + 1):
                    seat_id = f"seat-{seat_number}"
                    status = "available"
                    self.session.execute(query, (show_id, seat_id, seat_number, status))
            except Exception as e:
                print(f"Error populating seats for show {show_id}: {e}", file=sys.stderr)

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):
		return jsonify({'description': 'Cassandra Theatre API'})


@app.route('/shows', methods = ['GET'])
def get_shows():
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
                return jsonify({'message': 'Show added successfully', 'show_id': show_id}), 201
            except Exception as e:
                return jsonify({'error': f'Could not add show: {e}'}), 500
        

if __name__ == '__main__':

	app.run(debug = True,host='0.0.0.0', port=8080)