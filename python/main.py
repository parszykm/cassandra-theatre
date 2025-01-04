from flask import Flask, jsonify, request
from cassandra.cluster import Cluster
import configparser
import sys

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
        query = "SELECT * FROM shows"
        rows = self.session.execute(query)
        return [{"show_id": str(row.show_id),
                 "show_date": str(row.show_date),
                 "show_time": str(row.show_time),
                 "title": row.title} for row in rows]

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):
		return jsonify({'description': 'Cassandra Theatre API'})


@app.route('/shows', methods = ['GET'])
def get_shows():
	backend = BackendSession()
	shows = backend.get_all_shows()
	return jsonify({'shows': shows})

if __name__ == '__main__':

	app.run(debug = True,host='0.0.0.0', port=8080)